# Task: Issue #247 — Wire Cherenkov Trace signing into scan pipeline

**Branch:** `feat/247-trace-signing`
**Labels:** `priority:critical, feature, phase-3, area:infra`
**Milestone:** v1.5.0
**PR must contain:** `Closes #247`

## Context

The TOKAMAK invariant requires that every PoC execution result carry a cryptographic
signature: `trace_hash = sha256(output + timestamp)`. This must be wired into the
scan aggregation pipeline so that every scan result is automatically signed and persisted.

**Depends on:** #237 (aggregator), #246 (SQLite WAL logger)

## Context files

```
packages/cherenkov/core/aggregator.py          ← aggregate_scans() — wire signing here
packages/cherenkov/core/storage/database.py    ← save_trace(), compute_trace_hash()
packages/cherenkov/core/tokamak.py             ← TOKAMAK sandbox reference
packages/cherenkov/api/main.py                 ← scan endpoint — return trace_hash
```

## What to do

1. **Wire trace signing into the aggregator pipeline**:

   ```python
   # In packages/cherenkov/core/aggregator.py — add to aggregate_scans()
   from cherenkov.core.storage.database import init_db, save_trace

   async def aggregate_scans(
       scanners: list[BaseScanner],
       target: str,
       timeout: float = 30.0,
       persist: bool = True,
   ) -> AggregatedResult:
       # ... existing aggregation logic ...

       # After aggregation, persist each scanner result as a signed trace
       trace_hashes: list[str] = []
       if persist:
           conn = init_db()
           for result in results:
               if not isinstance(result, Exception):
                   trace_hash = save_trace(conn, result)
                   trace_hashes.append(trace_hash)
           conn.close()

       return AggregatedResult(
           target=target,
           findings=deduped,
           scanner_names=scanner_names,
           total_duration_ms=(time.monotonic() - start) * 1000,
           deduplicated_count=raw_count - len(deduped),
           trace_hashes=trace_hashes,  # NEW field
       )
   ```

2. **Update `AggregatedResult` dataclass** to include `trace_hashes`:
   ```python
   @dataclass
   class AggregatedResult:
       target: str
       findings: list[Finding] = field(default_factory=list)
       scanner_names: list[str] = field(default_factory=list)
       total_duration_ms: float = 0.0
       deduplicated_count: int = 0
       trace_hashes: list[str] = field(default_factory=list)  # NEW
   ```

3. **Update the scan endpoint** to return trace hashes:
   ```python
   # In main.py ScanResponse
   class ScanResponse(BaseModel):
       # ... existing fields ...
       trace_hashes: list[str] = []
   ```

4. **Write tests**:
   ```python
   # tests/unit/test_trace_signing.py
   import pytest
   import tempfile
   from pathlib import Path
   from cherenkov.core.storage.database import compute_trace_hash, init_db, save_trace

   def test_trace_hash_is_sha256():
       # Create a mock ScanResult, compute hash, verify format
       ...

   def test_trace_hash_is_deterministic_per_content():
       # Same content = different hash (timestamp differs)
       # This is expected — each invocation is unique
       ...

   def test_save_trace_persists_to_db():
       ...
   ```

## Files to modify

- `packages/cherenkov/core/aggregator.py` — wire trace signing after aggregation
- `packages/cherenkov/core/storage/database.py` — ensure `compute_trace_hash` + `save_trace` exist
- `packages/cherenkov/api/main.py` — expose `trace_hashes` in response
- `tests/unit/test_trace_signing.py` — NEW

## Verify

```bash
ruff format packages/ && ruff check packages/ --ignore W,S,B
pytest tests/unit/test_trace_signing.py tests/unit/test_sqlite_wal.py tests/unit/test_aggregator.py -v

# End-to-end smoke test
python -c "
import hashlib
test_hash = hashlib.sha256(b'test_output_2026-05-23T00:00:00Z').hexdigest()
assert len(test_hash) == 64, 'SHA-256 should be 64 hex chars'
print(f'Trace hash format OK: {test_hash[:16]}...')
print('PASS')
"
```
