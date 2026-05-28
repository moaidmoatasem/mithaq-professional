import sys
from unittest.mock import MagicMock

class MockPsutil:
    def __init__(self):
        self.__spec__ = MagicMock()
    def cpu_count(self, logical=False):
        return 8
    def virtual_memory(self):
        class Mem:
            total = 16e9
        return Mem()
sys.modules['psutil'] = MockPsutil()




from unittest.mock import patch

import pytest
from cherenkov.api.main import app
from fastapi import WebSocketDisconnect
from fastapi.testclient import TestClient


@patch("asyncio.sleep", side_effect=WebSocketDisconnect)
def test_websocket_live(mock_sleep):
    client = TestClient(app)
    with client.websocket_connect("/ws/live") as websocket:
        data = websocket.receive_json()
        assert data["event"] == "health_pulse"
        assert "timestamp" in data
        assert data["queue_depth"] == 0
        assert data["active_scans"] == 0
