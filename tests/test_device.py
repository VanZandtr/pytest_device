import sys
import os
import logging
import pytest
from src.device import DeviceController, DeviceNotReadyError, DeviceTimeoutError
from abc import ABC, abstractmethod
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Configure logging at the module level
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_log.log", mode="w"),
        logging.StreamHandler()  # This will also print to console
    ]
)

logger = logging.getLogger(__name__)

class AbstractHardware(ABC):
    @abstractmethod
    def power_on(self):
        pass

    @abstractmethod
    def power_off(self):
        pass

    @abstractmethod
    def status(self):
        pass

    @abstractmethod
    def send(self, command):
        pass


# --- Fixture for default fake hardware (ready instantly) ---
@pytest.fixture
def fake_motionsensor_hw():
    return FakeMotionSensor()

@pytest.fixture
def fake_contactsensor_hw():
    return FakeContactSensor()

# --- Fixture for a controller with instantly ready hardware ---
@pytest.fixture(params=["motion","contact"])
def device_controller(request, fake_motionsensor_hw, fake_contactsensor_hw):
    if request.param == "motion":
        return DeviceController(fake_motionsensor_hw)
    elif request.param == "contact":
        return DeviceController(fake_contactsensor_hw)
    else:
        raise ValueError("Invalid device type")

# --- Fixture for hardware that delays readiness, but doesn't fail boot ---
@pytest.fixture
def delayed_motion_hw():
    return FakeMotionSensor(ready_after=2)

@pytest.fixture
def delayed_contact_hw():
    return FakeContactSensor(ready_after=2)

# --- Fixture for controller with delayed hardware ---
@pytest.fixture(params=["motion","contact"])
def delayed_device_controller(request, delayed_motion_hw, delayed_contact_hw):
    if request.param == "motion":
        return DeviceController(delayed_motion_hw)
    elif request.param == "contact":
        return DeviceController(delayed_contact_hw)
    else:
        raise ValueError("Invalid device type")

# --- Fixture for hardware that never becomes ready ---
@pytest.fixture
def failing_motion_hw():
    return FakeMotionSensor(ready_after=10)

@pytest.fixture
def failing_contact_hw():
    return FakeContactSensor(ready_after=10)

# --- Fixture for controller with failing hardware ---
@pytest.fixture(params=["motion","contact"])
def failing_device_controller(request, failing_motion_hw, failing_contact_hw):
    if request.param == "motion":
        return DeviceController(failing_motion_hw)
    elif request.param == "contact":
        return DeviceController(failing_contact_hw)
    else:
        raise ValueError("Invalid device type")

##############################################################################################################

class FakeMotionSensor(AbstractHardware):
    def __init__(self, ready_after=0):
        self._power = False
        self._ready_counter = 0
        self._ready_after = ready_after
        self.commands = []
        self._motion_detected = False

    def power_on(self):
        self._power = True
        self._ready_counter += 1

    def power_off(self):
        self._power = False

    def status(self):
        if self._ready_counter > self._ready_after:
            return "READY"
        return "BOOTING"
    
    def send(self, cmd):
        if not self._power:
            raise DeviceNotReadyError("Device is not powered on")
        if self._ready_counter <= self._ready_after:
            raise DeviceTimeoutError("Device is not ready")
        self.commands.append(cmd)
        
        # Special commands processing
        if cmd == "GET_MOTION":
            return "MOTION:YES" if self._motion_detected else "MOTION:NO"
        
        return f"ACK:{cmd}"
    
    def set_motion_detected(self, detected=True):
        """Set the motion detection state for testing"""
        self._motion_detected = detected

class FakeContactSensor(AbstractHardware):
    def __init__(self, ready_after=0):
        self._power = False
        self._ready_counter = 0
        self._ready_after = ready_after
        self.commands = []
        self._contact_state = "CLOSED"  # Default state is closed

    def power_on(self):
        self._power = True
        self._ready_counter += 1

    def power_off(self):
        self._power = False

    def status(self):
        if self._ready_counter > self._ready_after:
            return "READY"
        return "BOOTING"
    
    def send(self, cmd):
        if not self._power:
            raise DeviceNotReadyError("Device is not powered on")
        if self._ready_counter <= self._ready_after:
            raise DeviceTimeoutError("Device is not ready")
        self.commands.append(cmd)
        
        # Special commands processing
        if cmd == "GET_CONTACT":
            return f"CONTACT:{self._contact_state}"
        
        return f"ACK:{cmd}"
    
    def set_contact_state(self, state):
        """Set the contact sensor state for testing. State should be 'OPEN' or 'CLOSED'"""
        if state not in ["OPEN", "CLOSED"]:
            raise ValueError("Contact state must be either 'OPEN' or 'CLOSED'")
        self._contact_state = state

##############################################################################################################       

def test_device_boots_first_try(device_controller):
    logger.info("Test device boots first try...")
    device_controller.boot_device()
    assert device_controller.ready

def test_device_requires_multiple_boots(delayed_device_controller):
    logger.info("Test device requires multiple boots...")
    delayed_device_controller.boot_device()
    assert delayed_device_controller.ready

def test_device_fails_to_boot(failing_device_controller):
    logger.info("Test device fails to boot...")
    with pytest.raises(DeviceTimeoutError):
        failing_device_controller.boot_device()

def test_command_before_boot(device_controller):
    logger.info("Test command before boot...")
    with pytest.raises(DeviceNotReadyError):
        device_controller.send_command("PING")

def test_successful_command_after_boot(device_controller):
    logger.info("Test successful command after boot...")
    device_controller.boot_device()
    resp = device_controller.send_command("PING")
    assert resp == "ACK:PING"
    assert device_controller.ready

# --- Motion Sensor Specific Tests ---

@pytest.fixture
def motion_controller(fake_motionsensor_hw):
    controller = DeviceController(fake_motionsensor_hw)
    controller.boot_device()
    return controller

def test_motion_detection(motion_controller, fake_motionsensor_hw):
    logger.info("Testing motion detection...")
    
    # No motion initially
    assert not motion_controller.check_motion()
    
    # Set motion detected
    fake_motionsensor_hw.set_motion_detected(True)
    assert motion_controller.check_motion()
    
    # Reset motion state
    fake_motionsensor_hw.set_motion_detected(False)
    assert not motion_controller.check_motion()

def test_motion_detection_type_error(device_controller):
    # This only runs with contact sensors (due to parametrization in device_controller fixture)
    if "Contact" in device_controller.device_type:
        logger.info("Testing motion detection type error on contact sensor...")
        device_controller.boot_device()
        with pytest.raises(TypeError):
            device_controller.check_motion()

# --- Contact Sensor Specific Tests ---

@pytest.fixture
def contact_controller(fake_contactsensor_hw):
    controller = DeviceController(fake_contactsensor_hw)
    controller.boot_device()
    return controller

def test_contact_sensing(contact_controller, fake_contactsensor_hw):
    logger.info("Testing contact sensing...")
    
    # Default state is CLOSED
    assert contact_controller.check_contact() == "CLOSED"
    
    # Set to OPEN
    fake_contactsensor_hw.set_contact_state("OPEN")
    assert contact_controller.check_contact() == "OPEN"
    
    # Set back to CLOSED
    fake_contactsensor_hw.set_contact_state("CLOSED")
    assert contact_controller.check_contact() == "CLOSED"

def test_contact_sensing_type_error(device_controller):
    # This only runs with motion sensors (due to parametrization in device_controller fixture)
    if "Motion" in device_controller.device_type:
        logger.info("Testing contact sensing type error on motion sensor...")
        device_controller.boot_device()
        with pytest.raises(TypeError):
            device_controller.check_contact()

def test_contact_invalid_state(contact_controller, fake_contactsensor_hw):
    logger.info("Testing invalid contact state...")
    with pytest.raises(ValueError):
        fake_contactsensor_hw.set_contact_state("INVALID")