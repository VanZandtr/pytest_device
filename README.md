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