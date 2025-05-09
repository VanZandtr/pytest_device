# Firmware-Style Device Controller: Test Suite

This project simulates testing a basic firmware-level `DeviceController` class, with realistic boot behavior, state management, and command sending, all using Python and `pytest`.

---

## 📦 Project Structure
src/
└── device.py # Contains the DeviceController and custom exceptions

tests/
└── test_device.py # Tests the controller behavior using fake hardware


---

## 🧠 What the Code Does

The `DeviceController` class simulates a firmware device that:
- Powers on hardware and checks readiness.
- Raises errors if booting fails or commands are sent while not ready.
- Sends commands only after a successful boot.
- Powers off and resets state on shutdown.

The hardware interface is simulated using a `FakeHardware` class with:
- Configurable boot delays.
- Command storage.
- Status simulation ("BOOTING" vs "READY").

---

## ✅ What is Being Tested

Tests in `test_device.py` cover:

- ✅ Device boots successfully on first try.
- ✅ Device needs multiple attempts to boot.
- ✅ Device fails to boot (raises timeout error).
- ✅ Sending a command before boot fails (raises not-ready error).
- ✅ Sending a command after boot succeeds and returns ACK.
- ✅ Shutdown resets device readiness state.

All tests use dependency injection to simulate real hardware behavior using test fixtures.

---

## 🧪 How to Run the Tests

Make sure you have `pytest` installed:

```bash
pip install -r requirements-dev.txt
```

Then run:

```bash
python -m pytest -v
```
