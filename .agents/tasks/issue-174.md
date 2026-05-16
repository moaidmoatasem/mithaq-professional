# Task: Issue #174 — TOKAMAK Docker Sandbox

**Branch:** `feat/174-tokamak-docker-sandbox`
**Labels:** `feature, phase-2, area:infra, priority:high, security`
**PR must contain:** `Closes #174`

## Context files (read before coding)

```
packages/cherenkov/core/tokamak.py       ← 223-line stub to extend
Dockerfile.tokamak                        ← sandbox image
packages/cherenkov/core/base_scanner.py  ← ScanResult / Finding types
packages/cherenkov/api/main.py           ← add two endpoints here
```

## Implement

### 1. `packages/cherenkov/core/tokamak.py` — extend the stub

```python
from dataclasses import dataclass
from typing import Optional
import hashlib, json, subprocess, time, tempfile, os

@dataclass
class Command:
    payload: str
    scanner_name: str
    timeout_s: float = 30.0

@dataclass
class TokamakResult:
    stdout: str
    stderr: str
    exit_code: int
    trace_hash: str        # sha256(stdout+stderr+timestamp)
    shred_receipt: dict    # {"files_erased": [...], "timestamp": ..., "method": "overwrite+truncate"}
    duration_ms: float
```

`Tokamak.execute(command: Command) -> TokamakResult`:
- Write payload to a temp file
- `docker run --rm --network none -v <tmpdir>:/workspace <image> <cmd>`
- Hash: `sha256((stdout + stderr + iso_ts).encode()).hexdigest()`
- Shred: overwrite temp file with zeros, truncate, delete → emit receipt
- Return `TokamakResult`

### 2. `packages/cherenkov/api/main.py` — two endpoints under `v1` router

```python
@v1.post("/sandbox/execute")
async def v1_sandbox_execute(command: Command) -> dict: ...

@v1.get("/sandbox/status")
async def v1_sandbox_status() -> dict: ...
```

### 3. `tests/unit/test_tokamak.py` — mock subprocess

```python
from unittest.mock import patch, MagicMock
from cherenkov.core.tokamak import Tokamak, Command

def test_execute_signs_output():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout=b"ok", stderr=b"", returncode=0)
        result = Tokamak().execute(Command(payload="test", scanner_name="test"))
        assert len(result.trace_hash) == 64
        assert "files_erased" in result.shred_receipt
```

## Verify

```bash
ruff format packages/ && ruff check packages/ --ignore W,S,B
pytest tests/unit/test_tokamak.py -v
```
