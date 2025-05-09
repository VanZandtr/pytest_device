import time
import logging

logger = logging.getLogger(__name__)

class DeviceNotReadyError(Exception):
    pass

class DeviceTimeoutError(Exception):
    pass

class DeviceController:
    def __init__(self, hardware_interface):
        self.hw = hardware_interface
        self.ready = False
        # Determine device type based on class name
        self.device_type = hardware_interface.__class__.__name__

    def boot_device(self, retries=3, timeout=0.1):
        for i in range(retries):
            try:
                logger.info(f"Boot attempt {i+1}")
                self.hw.power_on()
                for j in range(10):  # wait up to 1s total per retry
                    status = self.hw.status()
                    logger.info(f"Status check {j+1}: {status}")
                    if status == "READY":
                        self.ready = True
                        logger.info(f"Device ready! Type: {self.device_type}")
                        return
                    time.sleep(timeout)
            except Exception as e:
                logger.error(f"Attempt {i+1} failed: {e}")
        
        logger.error("Device failed to boot after all retries")
        raise DeviceTimeoutError("Device failed to boot within the specified timeout.")
        
    def send_command(self, command):
        """Sends a command to the device."""
        if not self.ready:
            logger.error("Attempted to send command to device that is not ready")
            raise DeviceNotReadyError("Device is not ready.")
        logger.info(f"Sending command: {command}")
        return self.hw.send(command)
    
    def check_motion(self):
        """Check for motion detection (only for motion sensors)"""
        if "Motion" not in self.device_type:
            logger.error("Attempted to check motion on non-motion device")
            raise TypeError("This device does not support motion detection")
        if not self.ready:
            raise DeviceNotReadyError("Device is not ready.")
        
        logger.info("Checking motion status")
        response = self.hw.send("GET_MOTION")
        return response == "MOTION:YES"
    
    def check_contact(self):
        """Check contact state (only for contact sensors)"""
        if "Contact" not in self.device_type:
            logger.error("Attempted to check contact on non-contact device")
            raise TypeError("This device does not support contact sensing")
        if not self.ready:
            raise DeviceNotReadyError("Device is not ready.")
        
        logger.info("Checking contact status")
        response = self.hw.send("GET_CONTACT")
        return response.split(":")[1]  # Returns "OPEN" or "CLOSED"

    def shutdown(self):
        logger.info("Shutting down device")
        self.hw.power_off()
        self.ready = False