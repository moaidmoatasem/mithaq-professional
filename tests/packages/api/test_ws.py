from unittest.mock import patch

import pytest
from cherenkov.api.main import app
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketDisconnect


def test_ws_live():
    client = TestClient(app)

    with patch("asyncio.sleep", side_effect=WebSocketDisconnect):
        try:
            with client.websocket_connect("/ws/live") as websocket:
                data = websocket.receive_json()
                assert data["event"] == "health_pulse"
                assert "timestamp" in data
                assert data["queue_depth"] == 0
                assert data["active_scans"] == 0
        except WebSocketDisconnect:
            pass
