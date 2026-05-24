# Task: Issue #246 — TOKAMAK SQLite WAL logger

**Branch:** `feat/246-sqlite-wal`
**Labels:** `priority:critical, feature, phase-3, area:infra`
**Milestone:** v1.5.0
**PR must contain:** `Closes #246`

## Context

All security findings ("Cherenkov Traces") must be persisted to a local SQLite database
operating in WAL (Write-Ahead Logging) mode for crash resilience and concurrent read access.
This is foundational infrastructure for the TOKAMAK execution pipeline.

## Context files

```
packages/cherenkov/core/storage/database.py    ← existing helpers (init_db, save_scan)
packages/cherenkov/core/tokamak.py             ← TOKAMAK sandbox — consumes traces
packages/cherenkov/core/base_scanner.py        ← ScanResult, Finding dataclasses
```

## What to do

1. **Update `packages/cherenkov/core/storage/database.py`** to use WAL mode:

   ```python
   """SQLite WAL-mode persistence for Cherenkov Traces."""
   from __future__ import annotations

   import json
   import sqlite3
   import hashlib
   from datetime import datetime, timezone
   from pathlib import Path
   from cherenkov.core.base_scanner import ScanResult, Finding

   DEFAULT_DB_PATH = Path("data/cherenkov_traces.sqlite")

   def init_db(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
       """Initialize SQLite database in WAL mode."""
       db_path.parent.mkdir(parents=True, exist_ok=True)
       conn = sqlite3.connect(str(db_path))
       conn.execute("PRAGMA journal_mode=WAL")
       conn.execute("PRAGMA synchronous=NORMAL")
       conn.execute("PRAGMA busy_timeout=5000")

       conn.executescript("""
           CREATE TABLE IF NOT EXISTS cherenkov_traces (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               trace_hash TEXT NOT NULL UNIQUE,
               target TEXT NOT NULL,
               scanner_name TEXT NOT NULL,
               findings_json TEXT NOT NULL,
               finding_count INTEGER NOT NULL,
               duration_ms REAL,
               created_at TEXT NOT NULL DEFAULT (datetime('now')),
               metadata_json TEXT
           );

           CREATE INDEX IF NOT EXISTS idx_traces_target ON cherenkov_traces(target);
           CREATE INDEX IF NOT EXISTS idx_traces_scanner ON cherenkov_traces(scanner_name);
           CREATE INDEX IF NOT EXISTS idx_traces_created ON cherenkov_traces(created_at);
       """)
       conn.commit()
       return conn

   def compute_trace_hash(result: ScanResult) -> str:
       """SHA-256 hash of scan output + timestamp (TOKAMAK signing)."""
       payload = json.dumps({
           "target": result.target,
           "scanner": result.scanner_name,
           "findings": [f.__dict__ for f in result.findings],
           "timestamp": datetime.now(timezone.utc).isoformat(),
       }, sort_keys=True)
       return hashlib.sha256(payload.encode()).hexdigest()

   def save_trace(conn: sqlite3.Connection, result: ScanResult) -> str:
       """Persist a ScanResult as a Cherenkov Trace. Returns trace_hash."""
       trace_hash = compute_trace_hash(result)
       findings_json = json.dumps([f.__dict__ for f in result.findings])

       conn.execute(
           """INSERT OR REPLACE INTO cherenkov_traces
              (trace_hash, target, scanner_name, findings_json, finding_count, duration_ms)
              VALUES (?, ?, ?, ?, ?, ?)""",
           (trace_hash, result.target, result.scanner_name,
            findings_json, len(result.findings), result.duration_ms),
       )
       conn.commit()
       return trace_hash

   def get_traces(conn: sqlite3.Connection, target: str | None = None,
                  limit: int = 100) -> list[dict]:
       """Retrieve stored traces, optionally filtered by target."""
       if target:
           cursor = conn.execute(
               "SELECT * FROM cherenkov_traces WHERE target = ? ORDER BY created_at DESC LIMIT ?",
               (target, limit),
           )
       else:
           cursor = conn.execute(
               "SELECT * FROM cherenkov_traces ORDER BY created_at DESC LIMIT ?",
               (limit,),
           )
       columns = [desc[0] for desc in cursor.description]
       return [dict(zip(columns, row)) for row in cursor.fetchall()]
   ```

2. **Write tests** at `tests/unit/test_sqlite_wal.py`:
   ```python
   import pytest
   import tempfile
   from pathlib import Path
   from cherenkov.core.storage.database import init_db, save_trace, get_traces

   def test_init_db_creates_wal_mode():
       with tempfile.TemporaryDirectory() as tmp:
           db_path = Path(tmp) / "test.sqlite"
           conn = init_db(db_path)
           mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
           assert mode == "wal"
           conn.close()

   def test_save_and_retrieve_trace():
       ...
   ```

3. **Add `data/` to `.gitignore`** if not already (prevent committing .sqlite files)

## Files to modify

- `packages/cherenkov/core/storage/database.py` — update with WAL mode + trace schema
- `tests/unit/test_sqlite_wal.py` — NEW
- `.gitignore` — add `*.sqlite` pattern (if not done in #234)

## Verify

```bash
ruff format packages/ && ruff check packages/ --ignore W,S,B
pytest tests/unit/test_sqlite_wal.py -v

# Smoke test WAL mode
python -c "
from cherenkov.core.storage.database import init_db
import tempfile, pathlib
conn = init_db(pathlib.Path(tempfile.mktemp(suffix='.sqlite')))
mode = conn.execute('PRAGMA journal_mode').fetchone()[0]
print(f'Journal mode: {mode}')
assert mode == 'wal', f'Expected WAL, got {mode}'
print('PASS')
conn.close()
"
```
