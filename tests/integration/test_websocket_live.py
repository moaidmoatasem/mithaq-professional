import pytest
import json
from unittest.mock import patch
from fastapi.testclient import TestClient
from cherenkov.api.main import app

def test_websocket_live(monkeypatch):
    import cherenkov.api.main as main_module

    # We don't want the real background loop to keep going forever and blocking TestClient exit
    # TestClient doesn't cancel background tasks immediately if they are created with asyncio.create_task and don't exit.

    # Let's mock the _health_pulse_loop so it only sends 2 pulses then exits, preventing hangs.
    original_pulse_loop = main_module._health_pulse_loop

    async def mock_pulse_loop(websocket):
        for _ in range(3):
            # No sleep needed for test
            await websocket.send_text(json.dumps({"type": "health_pulse"}))

    monkeypatch.setattr(main_module, "_health_pulse_loop", mock_pulse_loop)

    with TestClient(app) as client:
        with client.websocket_connect("/ws/live") as websocket:
            data1 = websocket.receive_json()
            assert data1["event"] == "health_pulse"

            data2 = websocket.receive_json()
            assert data2["event"] == "health_pulse"

            websocket.send_json({"command": "subscribe_scan", "scan_id": "test-123"})
            websocket.send_json({"command": "unsubscribe_scan", "scan_id": "test-123"})
