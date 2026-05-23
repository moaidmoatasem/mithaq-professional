# Task: Issue #238 — FastAPI POST /api/v1/scan — wire aggregator

**Branch:** `feat/238-scan-endpoint`
**Labels:** `priority:high, feature, phase-2, area:api`
**Milestone:** v1.1.0
**PR must contain:** `Closes #238`

## Context

The `/api/v1/scan` endpoint needs to be wired to the scanner registry and aggregator
so that a single POST request runs all registered scanners against a target URL,
aggregates the results, and returns a unified response.

**Depends on:** #236 (registry), #237 (aggregator)

## Context files

```
packages/cherenkov/api/main.py             ← FastAPI app — add/update endpoint
packages/cherenkov/core/registry.py        ← ScannerRegistry.all()
packages/cherenkov/core/aggregator.py      ← aggregate_scans()
packages/cherenkov/core/base_scanner.py    ← ScanResult, Finding types
```

## What to do

1. **Add or update POST `/api/v1/scan` endpoint** in `main.py`:

   ```python
   from pydantic import BaseModel, HttpUrl
   from cherenkov.core.registry import registry
   from cherenkov.core.aggregator import aggregate_scans

   class ScanRequest(BaseModel):
       target: str  # URL to scan
       timeout: float = 30.0

   class ScanResponse(BaseModel):
       target: str
       scanner_count: int
       finding_count: int
       deduplicated_count: int
       duration_ms: float
       findings: list[dict]  # Serialized Finding objects

   @app.post("/api/v1/scan", response_model=ScanResponse)
   async def run_scan(req: ScanRequest):
       scanners = registry.all()
       if not scanners:
           registry.discover()
           scanners = registry.all()

       result = await aggregate_scans(scanners, req.target, timeout=req.timeout)

       return ScanResponse(
           target=result.target,
           scanner_count=len(result.scanner_names),
           finding_count=len(result.findings),
           deduplicated_count=result.deduplicated_count,
           duration_ms=result.total_duration_ms,
           findings=[f.__dict__ for f in result.findings],
       )
   ```

2. **Ensure registry.discover()** is called in the FastAPI lifespan/startup event:
   ```python
   @app.on_event("startup")
   async def startup():
       registry.discover()
   ```

3. **Write integration test**:
   ```python
   # tests/integration/test_scan_endpoint.py
   import pytest
   from httpx import AsyncClient, ASGITransport
   from cherenkov.api.main import app

   @pytest.mark.asyncio
   @pytest.mark.integration
   async def test_scan_endpoint_returns_results():
       transport = ASGITransport(app=app)
       async with AsyncClient(transport=transport, base_url="http://test") as client:
           resp = await client.post("/api/v1/scan", json={"target": "http://example.com"})
       assert resp.status_code == 200
       data = resp.json()
       assert "findings" in data
       assert data["target"] == "http://example.com"
   ```

## Files to modify

- `packages/cherenkov/api/main.py` — add/update scan endpoint + startup discovery
- `tests/integration/test_scan_endpoint.py` — NEW

## Verify

```bash
ruff format packages/ && ruff check packages/ --ignore W,S,B
pytest tests/unit/test_aggregator.py tests/unit/test_scanner_registry.py -v
pytest tests/integration/test_scan_endpoint.py -v -m integration

# Manual smoke test
# uvicorn cherenkov.api.main:app --port 8000 &
# curl -X POST http://localhost:8000/api/v1/scan -H 'Content-Type: application/json' -d '{"target":"http://example.com"}'
```
