
import time

class DeviceNotReadyError(Exception):
    pass

class DeviceTimeoutError(Exception):
    pass

class DeviceController:
    def __init__(self, hardware_interface):
        self.hw = hardware_interface
        self.ready = False

    def boot_device(self, retries=3, timeout=0.1):
        """Attempts to boot the device and waits for it to become ready."""
        for I in range(retries):
            try:
                self.hw.power_on()
                if self.hw.status() == "READY":
                    self.ready = True
                    return
            except Exception as e:
                print(f"Attempt {i+1} failed: {e}")
                time.sleep(timeout)
        raise DeviceTimeoutError("Device failed to boot within the specified timeout.")
        
    def send_command(self, command):
        """Sends a command to the device."""
        if not self.ready:
            raise DeviceNotReadyError("Device is not ready.")
        return self.hw.send(command)

    def shutdown(self):
        self.hw.power_off()
        self.ready = False
