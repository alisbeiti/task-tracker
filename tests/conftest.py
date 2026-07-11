import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import storage
from app.main import app


@pytest.fixture(autouse=True)
def _reset_storage() -> None:
    storage._reset()
    yield
    storage._reset()


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def created_task(client: TestClient) -> dict:
    response = client.post("/tasks", json={"title": "fixture task"})
    assert response.status_code == 201
    return response.json()
