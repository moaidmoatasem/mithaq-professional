import asyncio
from pathlib import Path

import cherenkov.core.storage.database as db
import pytest
from cherenkov.api.main import app
from cherenkov.core.storage.database import init_db
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def bypass_rate_limit():
    app.state.limiter.enabled = False
    yield
    app.state.limiter.enabled = True


@pytest.fixture(autouse=True)
def isolate_db(tmp_path: Path):
    test_db = tmp_path / "test_api.db"
    original_db = db._DB_PATH
    db._DB_PATH = test_db
    init_db(test_db)
    yield
    db._DB_PATH = original_db


@pytest.fixture(autouse=True)
def mock_external_deps(monkeypatch):
    async def mock_ollama():
        return "online"

    async def mock_qdrant():
        return "online"

    monkeypatch.setattr("cherenkov.api.main._check_ollama", mock_ollama)
    monkeypatch.setattr("cherenkov.api.main._check_qdrant", mock_qdrant)

    # Mock Redis (if used anywhere in the system, like for queue/cache)
    class DummyRedis:
        def get(self, key):
            return None

        def set(self, key, value):
            pass

    # It's not explicitly in main.py, but mock it generically in sys.modules if needed.
    # Alternatively, if there's a specific redis client, patch it.


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    assert "nodes" in data
    assert data["nodes"]["tensor"]["status"] == "online"
    assert data["nodes"]["lattice"]["status"] == "online"


def test_ablation_stats(client):
    response = client.get("/api/v1/ablation/stats")
    assert response.status_code == 200
    data = response.json()
    assert "session_stats" in data
    assert "attempts" in data["session_stats"]
    assert "drops" in data["session_stats"]


def test_auth_token_and_me(client):
    # Test getting a token with default admin credentials
    auth_data = {"username": "admin", "password": "admin"}
    response = client.post("/api/v1/auth/token", json=auth_data)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    token = token_data["access_token"]

    # Test getting current user with token
    headers = {"Authorization": f"Bearer {token}"}
    response_me = client.get("/api/v1/auth/me", headers=headers)
    assert response_me.status_code == 200
    me_data = response_me.json()
    assert me_data["username"] == "admin"


def test_scan_post(client, monkeypatch):
    # Mock _run_scan to return a dummy result instead of starting actual scans
    async def mock_run_scan(request, background_tasks):
        from datetime import datetime, timezone

        return {
            "status": "accepted",
            "scan_id": "test_scan_123",
            "target": request.url,
            "count": 0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    monkeypatch.setattr("cherenkov.api.main._run_scan", mock_run_scan)

    # Need authentication for v1_scan
    auth_data = {"username": "admin", "password": "admin"}
    token_response = client.post("/api/v1/auth/token", json=auth_data)
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    scan_payload = {"url": "http://example.com"}
    response = client.post("/api/v1/scan", json=scan_payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "accepted"
    assert data["scan_id"] == "test_scan_123"
    assert data["target"] == "http://example.com"


def test_websocket_live(client, monkeypatch):
    from fastapi.websockets import WebSocketDisconnect

    call_count = 0

    async def mock_sleep(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count > 2:
            raise WebSocketDisconnect()
        return

    monkeypatch.setattr(asyncio, "sleep", mock_sleep)

    with client.websocket_connect("/ws/live") as websocket:
        data1 = websocket.receive_json()
        assert data1["event"] == "health_pulse"

        data2 = websocket.receive_json()
        assert data2["event"] == "health_pulse"


def test_error_cases(client):
    # Get a token to bypass 401 for the 422 test
    auth_data = {"username": "admin", "password": "admin"}
    token_response = client.post("/api/v1/auth/token", json=auth_data)
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 422: Malformed payload
    response_422 = client.post("/api/v1/scan", json={"invalid_field": "123"}, headers=headers)
    assert response_422.status_code == 422

    # 401: Unauthorized access
    response_401 = client.get("/api/v1/auth/me")
    assert response_401.status_code == 401

    # 404: Not found
    response_404 = client.get("/api/v1/non_existent_route")
    assert response_404.status_code == 404
