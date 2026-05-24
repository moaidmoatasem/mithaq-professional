import pytest
from cherenkov.api.main import app
from fastapi.testclient import TestClient


from unittest.mock import patch
from fastapi import WebSocketDisconnect

@patch("asyncio.sleep", side_effect=WebSocketDisconnect)
def test_websocket_live(mock_sleep):
    client = TestClient(app)
    with client.websocket_connect("/ws/live") as websocket:
        data = websocket.receive_json()
        assert data["event"] == "health_pulse"
        assert "timestamp" in data
        assert data["queue_depth"] == 0
        assert data["active_scans"] == 0
