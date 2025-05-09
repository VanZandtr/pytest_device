import pytest

@pytest.fixture(scope="session")
def global_data():
    # Setup that runs once for the entire test session
    data = {"config": "test_settings"}
    yield data
    # Teardown code goes here