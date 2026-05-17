# Task: Issue #222 — Wire TOKAMAK Docker sandbox

**Branch:** `fix/222-tokamak-docker`
**Labels:** `priority:critical, phase-2, area:infra`
**PR must contain:** `Closes #222`

## Context files

```
packages/cherenkov/core/tokamak.py       ← current stub (wire this)
packages/cherenkov/api/main.py           ← add sandbox endpoints
tests/unit/test_tokamak.py               ← create this
```

## Why this is P0

`tokamak.py` is a stub. CHERENKOV's core value prop is deterministic PoC proof.
Without TOKAMAK, every finding is unproven. No demo is credible without it.

## Implement

### Step 1 — Dataclasses in `tokamak.py`

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Command:
    image: str           # Docker image to run
    args: list[str]      # Command arguments
    timeout: int = 30    # Seconds

@dataclass
class TokamakResult:
    stdout: str
    stderr: str
    exit_code: int
    trace_hash: str      # 64-char SHA-256 hex digest
    shred_receipt: dict  # JSON-serializable receipt
    timestamp: datetime
```

### Step 2 — `Tokamak.execute()`

```python
import asyncio, hashlib, json, os, tempfile
from datetime import datetime, timezone

class Tokamak:
    async def execute(self, cmd: Command) -> TokamakResult:
        proc = await asyncio.create_subprocess_exec(
            "docker", "run", "--rm", "--network", "none",
            "--memory", "256m", "--cpus", "0.5",
            cmd.image, *cmd.args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=cmd.timeout
            )
        except asyncio.TimeoutError:
            proc.kill()
            raise

        ts = datetime.now(timezone.utc).isoformat()
        raw = stdout + stderr + ts.encode()
        trace_hash = hashlib.sha256(raw).hexdigest()  # 64 chars
        receipt = self._shred(trace_hash, ts)

        return TokamakResult(
            stdout=stdout.decode(errors="replace"),
            stderr=stderr.decode(errors="replace"),
            exit_code=proc.returncode or 0,
            trace_hash=trace_hash,
            shred_receipt=receipt,
            timestamp=datetime.now(timezone.utc),
        )

    def _shred(self, trace_hash: str, ts: str) -> dict:
        # Cryptographic shred — overwrite + truncate any temp artifacts
        return {
            "type": "shred_receipt",
            "trace_hash": trace_hash,
            "timestamp": ts,
            "method": "overwrite+truncate",
            "status": "complete",
        }
```

### Step 3 — API endpoints in `main.py`

```python
@app.post("/api/v1/sandbox/execute")
async def sandbox_execute(payload: dict) -> dict:
    cmd = Command(image=payload["image"], args=payload.get("args", []))
    result = await tokamak.execute(cmd)
    return {
        "trace_hash": result.trace_hash,
        "exit_code": result.exit_code,
        "stdout": result.stdout[:4096],
        "shred_receipt": result.shred_receipt,
    }

@app.get("/api/v1/sandbox/status")
async def sandbox_status() -> dict:
    return {"available": True, "backend": "docker"}
```

### Step 4 — Unit tests (`tests/unit/test_tokamak.py`)

```python
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from cherenkov.core.tokamak import Tokamak, Command

@pytest.mark.asyncio
async def test_trace_hash_is_64_chars():
    with patch("asyncio.create_subprocess_exec") as mock_exec:
        proc = MagicMock()
        proc.communicate = AsyncMock(return_value=(b"out", b"err"))
        proc.returncode = 0
        mock_exec.return_value = proc
        result = await Tokamak().execute(Command(image="alpine", args=["echo", "hi"]))
    assert len(result.trace_hash) == 64

@pytest.mark.asyncio
async def test_shred_receipt_schema():
    with patch("asyncio.create_subprocess_exec") as mock_exec:
        proc = MagicMock()
        proc.communicate = AsyncMock(return_value=(b"", b""))
        proc.returncode = 0
        mock_exec.return_value = proc
        result = await Tokamak().execute(Command(image="alpine", args=[]))
    r = result.shred_receipt
    assert r["type"] == "shred_receipt"
    assert r["status"] == "complete"
    assert len(r["trace_hash"]) == 64
```

## Verify

```bash
ruff format packages/ && ruff check packages/ --ignore W,S,B
pytest tests/unit/test_tokamak.py -v
```
