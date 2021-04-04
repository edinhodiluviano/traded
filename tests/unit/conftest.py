import pytest
from fastapi.testclient import TestClient

import traded


@pytest.fixture
def client():
    client = TestClient(traded.main.app)
    yield client
