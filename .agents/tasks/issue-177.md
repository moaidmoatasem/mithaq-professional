# Task: Issue #177 — SQLite persistence + real health metrics

**Branch:** `feat/177-sqlite-health-metrics`
**Labels:** `feature, phase-2, area:api, priority:high`
**PR must contain:** `Closes #177`

## Context files

```
packages/cherenkov/api/main.py            ← _scan_history list + /health endpoint
packages/cherenkov/core/storage/database.py ← init_db, save_scan, SQLite helpers
packages/cherenkov/core/circuit_breaker.py  ← meissner_hub, CircuitBreakerRegistry
```

## Implement

### 1. `/api/v1/scans/history` — query SQLite instead of memory

In `database.py`, add:
```python
def list_scans(limit: int = 20) -> list[dict]:
    """Return last N scans newest-first."""
```

In `main.py`, replace the `_scan_history` list with a call to `list_scans(20)`.

### 2. `/api/v1/health` — real Ollama node check

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

Replace the static `"nodes"` dict — call `_check_ollama()` and populate each node's `status`.

### 3. Meissner state from circuit breaker

```python
from cherenkov.core.circuit_breaker import meissner_hub
# In v1_health():
meissner_state = meissner_hub.state.value.upper()  # "CLOSED" | "OPEN" | "HALF_OPEN"
```

### 4. Broadcast circuit_breaker WebSocket event

In `circuit_breaker.py`, add a callback hook to `Meissner._transition_to_open()`.
Register it from `main.py` at startup:

```python
from cherenkov.core.circuit_breaker import meissner_hub
meissner_hub.on_open(lambda: asyncio.create_task(
    _broadcast({"type": "circuit_breaker", "state": "OPEN", "reason": "threshold_exceeded"})
))
```

## Verify

```bash
ruff format packages/ && ruff check packages/ --ignore W,S,B
pytest tests/ -m "not (integration or ai_generated)" --tb=short
```
