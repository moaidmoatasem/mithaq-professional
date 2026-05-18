import json
import asyncio
from unittest.mock import patch

import pytest
from cherenkov.api.main import app
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketDisconnect

def test_websocket_live(monkeypatch):
    import cherenkov.api.main as main_module

    # TestClient doesn't cancel background tasks immediately if they are created with asyncio.create_task and don't exit.
    # The websocket loop in ws_live has `while True: ... await asyncio.sleep(5)` which runs forever.
    # To fix this, we mock asyncio.sleep to raise WebSocketDisconnect after the first couple of calls, forcing the loop to exit.

    call_count = 0
    async def mock_sleep(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count > 2:
            raise WebSocketDisconnect()
        return

    monkeypatch.setattr(asyncio, "sleep", mock_sleep)

    with TestClient(app) as client:
        with client.websocket_connect("/ws/live") as websocket:
            data1 = websocket.receive_json()
            assert data1["event"] == "health_pulse"

            data2 = websocket.receive_json()
            assert data2["event"] == "health_pulse"

            # we don't have these implemented in ws_live actually but let's just make sure it exits cleanly
            pass
