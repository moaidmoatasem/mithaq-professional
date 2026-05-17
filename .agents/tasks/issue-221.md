# Task: Issue #221 — Wire real health metrics

**Branch:** `fix/221-health-metrics`
**Labels:** `priority:critical, phase-2, area:api`
**PR must contain:** `Closes #221`

## Context files

```
packages/cherenkov/api/main.py            ← v1_health() — wire this
packages/cherenkov/core/circuit_breaker.py← meissner_hub (state source)
packages/cherenkov/core/storage/database.py← active scan query
```

## Why this is P0

The frontend HUD displays completely fake data. Every demo will show
"healthy / CLOSED / 0 active scans" regardless of reality.

## Implement

### Step 1 — Ollama ping helper

Add to `main.py`:

```python
import httpx

async def _check_ollama() -> str:
    try:
        async with httpx.AsyncClient(timeout=1.0) as c:
            r = await c.get("http://localhost:11434/api/tags")
            return "ready" if r.status_code == 200 else "offline"
    except Exception:
        return "offline"
```

### Step 2 — Real Meissner state

```python
from cherenkov.core.circuit_breaker import meissner_hub

# In v1_health():
meissner_state = meissner_hub.state.value.upper()  # "CLOSED" | "OPEN" | "HALF_OPEN"
```

### Step 3 — Real node response

Replace the static nodes dict:

```python
@app.get("/api/v1/health")
async def v1_health():
    ollama_status = await _check_ollama()
    meissner_state = meissner_hub.state.value.upper()

    return {
        "status": "operational" if ollama_status == "ready" else "degraded",
        "nodes": {
            "TENSOR": {"status": ollama_status, "model": "qwen2.5-coder:7b"},
            "KINETIC": {"status": ollama_status, "model": "qwen2.5-coder:1.5b-base"},
        },
        "meissner": {"state": meissner_state},
        "active_scans": len([s for s in _scan_history if s.get("status") == "running"]),
        "uptime": round(time.time() - _start_time),
    }
```

### Step 4 — Broadcast circuit_breaker WS event

In `circuit_breaker.py`, add callback hook to `Meissner`:

```python
def on_open(self, callback) -> None:
    self._on_open_callbacks.append(callback)

def _transition_to_open(self) -> None:
    # existing logic ...
    for cb in self._on_open_callbacks:
        cb()
```

Register from `main.py` at startup:

```python
import asyncio
from cherenkov.core.circuit_breaker import meissner_hub

@app.on_event("startup")
async def _register_ws_callbacks():
    meissner_hub.on_open(lambda: asyncio.create_task(
        _broadcast({"type": "circuit_breaker", "state": "OPEN", "reason": "threshold_exceeded"})
    ))
```

## Unit tests

```
tests/unit/test_api_health.py
```

```python
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch

@pytest.mark.asyncio
async def test_health_meissner_state():
    from cherenkov.api.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        with patch("cherenkov.api.main._check_ollama", return_value="offline"):
            r = await ac.get("/api/v1/health")
    assert r.status_code == 200
    data = r.json()
    assert data["meissner"]["state"] in ("CLOSED", "OPEN", "HALF_OPEN")
    assert data["status"] == "degraded"  # Ollama offline
```

## Verify

```bash
ruff format packages/ && ruff check packages/ --ignore W,S,B
pytest tests/unit/test_api_health.py -v
```
