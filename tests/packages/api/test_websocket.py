import pytest
from fastapi.testclient import TestClient
from cherenkov.api.main import app

def test_websocket_live():
    client = TestClient(app)
    with client.websocket_connect("/ws/live") as websocket:
        data = websocket.receive_json()
        assert data["event"] == "health_pulse"
        assert "timestamp" in data
        assert data["queue_depth"] == 0
        assert data["active_scans"] == 0
