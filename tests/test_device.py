import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import logging
import pytest
from src.device import DeviceController, DeviceNotReadyError, DeviceTimeoutError

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


# --- Fixture for default fake hardware (ready instantly) ---
@pytest.fixture
def fake_hw():
    return FakeHardware()

# --- Fixture for a controller with instantly ready hardware ---
@pytest.fixture
def controller(fake_hw):
    return DeviceController(fake_hw)

# --- Fixture for hardware that delays readiness, but doesn't fail boot ---
@pytest.fixture
def delayed_hw():
    return FakeHardware(ready_after=2)

# --- Fixture for controller with delayed hardware ---
@pytest.fixture
def delayed_controller(delayed_hw):
    return DeviceController(delayed_hw)

# --- Fixture for hardware that never becomes ready ---
@pytest.fixture
def failing_hw():
    return FakeHardware(ready_after=10)

# --- Fixture for controller with failing hardware ---
@pytest.fixture
def failing_controller(failing_hw):
    return DeviceController(failing_hw)

class FakeHardware:
    def __init__(self, ready_after=0):
        self._power = False
        self._ready_counter = 0
        self._ready_after = ready_after
        self.commands = []

    def power_on(self):
        self._power = True
        self._ready_counter += 1

    def power_off(self):
        self._power = False

    def status(self):
        if self._ready_counter > self._ready_after:
            return "READY"
        return "BOOTING"
    
    def send(self,cmd):
        if not self._power:
            raise DeviceNotReadyError("Device is not powered on")
        if self._ready_counter <= self._ready_after:
            raise DeviceTimeoutError("Device is not ready")
        self.commands.append(cmd)
        return f"ACK:{cmd}"

def test_device_boots_first_try(controller):
    logger.info("Test device boots first try...")
    controller.boot_device()
    assert controller.ready

def test_device_requires_multiple_boots(delayed_controller):
    logger.info("Test device requires multiple boots...")
    delayed_controller.boot_device()
    assert delayed_controller.ready

def test_device_fails_to_boot(failing_controller):
    logger.info("Test device fails to boot...")
    with pytest.raises(DeviceTimeoutError):
        failing_controller.boot_device()

def test_command_before_boot(controller):
    logger.info("Test command before boot...")
    with pytest.raises(DeviceNotReadyError):
        controller.send_command("PING")

def test_successful_command_after_boot(controller, fake_hw):
    logger.info("Test successful command after boot...")
    controller.boot_device()
    resp = controller.send_command("PING")
    assert resp == "ACK:PING"
    assert "PING" in fake_hw.commands
    assert controller.ready

def test_shutdown_clears_ready_state(controller):
    logger.info("Test shutdown clears ready state...")
    controller.boot_device()
    controller.shutdown()
    assert not controller.ready

