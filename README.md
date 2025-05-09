# Firmware-Style Device Controller: Test Suite

This project simulates testing a basic firmware-level `DeviceController` class, with realistic boot behavior, state management, and specialized sensor commands, all using Python and `pytest`.

## 📦 Project Structure

```
src/
└── device.py          # Contains the DeviceController and custom exceptions
tests/
└── test_device.py     # Tests the controller behavior using fake hardware
```

## 🧠 What the Code Does

The `DeviceController` class simulates a firmware device that:
* Powers on hardware and checks readiness
* Raises errors if booting fails or commands are sent while not ready
* Sends commands only after a successful boot
* Powers off and resets state on shutdown
* Detects device type and provides specialized methods for different sensor types

The system supports two types of devices:

1. **Motion Sensors**:
   * Can detect motion events
   * Provides `check_motion()` method that returns a boolean value

2. **Contact Sensors**:
   * Can track open/closed states
   * Provides `check_contact()` method that returns "OPEN" or "CLOSED" states

Hardware interfaces are simulated using fake classes with:
* Configurable boot delays
* Command storage
* Status simulation ("BOOTING" vs "READY")
* Sensor-specific state management

## ✅ What is Being Tested

Tests in `test_device.py` cover:

### Core Functionality
* ✅ Device boots successfully on first try
* ✅ Device needs multiple attempts to boot
* ✅ Device fails to boot (raises timeout error)
* ✅ Sending a command before boot fails (raises not-ready error)
* ✅ Sending a command after boot succeeds and returns ACK
* ✅ Shutdown resets device readiness state

### Motion Sensor Tests
* ✅ Motion detection state management
* ✅ Type error when calling motion methods on incompatible devices

### Contact Sensor Tests
* ✅ Contact state management (OPEN/CLOSED)
* ✅ Type error when calling contact methods on incompatible devices
* ✅ Validation of contact states

All tests use dependency injection via pytest fixtures to simulate real hardware behavior.

## 🛠️ Implementation Details

### Device Controller Features
* Device type detection based on hardware interface
* Type checking for specialized sensor methods
* Thorough error handling and logging
* Configurable boot retry mechanism

### Sensor Implementations
* Motion sensors: Set and check motion detection states
* Contact sensors: Set and check open/closed states with validation
* Both implement a common hardware interface for consistency

## 🧪 How to Run the Tests

Make sure you have `pytest` installed:

```
pip install -r requirements-dev.txt
```

Then run:

```
python -m pytest -v
```

## 📝 Example Usage

### Motion Sensor Example

```python
# Create a motion sensor controller
motion_hw = FakeMotionSensor()
controller = DeviceController(motion_hw)

# Boot the device
controller.boot_device()

# Check for motion
if controller.check_motion():
    print("Movement detected!")
else:
    print("No movement")
```

### Contact Sensor Example

```python
# Create a contact sensor controller
contact_hw = FakeContactSensor()
controller = DeviceController(contact_hw)

# Boot the device
controller.boot_device()

# Check contact state
state = controller.check_contact()
if state == "OPEN":
    print("Door is open!")
elif state == "CLOSED":
    print("Door is closed")
```
## Example Output

```python
$ python -m pytest --log-cli-level=INFO -v
========================================================================================================================================================= test session starts ========================================================================================================================================================== 
platform win32 -- Python 3.13.3, pytest-8.3.5, pluggy-1.5.0 -- C:\Users\vanzraym\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe
cachedir: .pytest_cache
metadata: {'Python': '3.13.3', 'Platform': 'Windows-11-10.0.26100-SP0', 'Packages': {'pytest': '8.3.5', 'pluggy': '1.5.0'}, 'Plugins': {'html': '4.1.1', 'metadata': '3.1.1'}}
rootdir: C:\Users\vanzraym\Documents\pytest example
configfile: pyproject.toml
tests/test_device.py::test_device_boots_first_try[contact] PASSED                                                                                                                                                                                                                                                                 [ 11%] 
tests/test_device.py::test_device_requires_multiple_boots[motion] PASSED                                                                                                                                                                                                                                                          [ 17%] 
tests/test_device.py::test_device_requires_multiple_boots[contact] PASSED                                                                                                                                                                                                                                                         [ 23%] 
tests/test_device.py::test_device_fails_to_boot[motion] PASSED                                                                                                                                                                                                                                                                    [ 29%] 
tests/test_device.py::test_device_fails_to_boot[contact] PASSED                                                                                                                                                                                                                                                                   [ 35%] 
tests/test_device.py::test_command_before_boot[motion] PASSED                                                                                                                                                                                                                                                                     [ 41%] 
tests/test_device.py::test_command_before_boot[contact] PASSED                                                                                                                                                                                                                                                                    [ 47%] 
tests/test_device.py::test_successful_command_after_boot[motion] PASSED                                                                                                                                                                                                                                                           [ 52%] 
tests/test_device.py::test_successful_command_after_boot[contact] PASSED                                                                                                                                                                                                                                                          [ 58%] 
tests/test_device.py::test_motion_detection PASSED                                                                                                                                                                                                                                                                                [ 64%] 
tests/test_device.py::test_motion_detection_type_error[motion] PASSED                                                                                                                                                                                                                                                             [ 70%] 
tests/test_device.py::test_motion_detection_type_error[contact] PASSED                                                                                                                                                                                                                                                            [ 76%] 
tests/test_device.py::test_contact_sensing PASSED                                                                                                                                                                                                                                                                                 [ 82%] 
tests/test_device.py::test_contact_sensing_type_error[motion] PASSED                                                                                                                                                                                                                                                              [ 88%] 
tests/test_device.py::test_contact_sensing_type_error[contact] PASSED                                                                                                                                                                                                                                                             [ 94%] 
tests/test_device.py::test_contact_invalid_state PASSED                                                                                                                                                                                                                                                                           [100%] 

========================================================================================================================================================= 17 passed in 10.27s ========================================================================================================================================================== 
```
