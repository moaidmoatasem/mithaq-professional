# Task: Issue #245 — Graduate/verify SSRF Scanner

**Branch:** `feat/245-ssrf-verify`
**Labels:** `priority:high, feature, phase-3, area:scanner`
**Milestone:** v1.5.0
**PR must contain:** `Closes #245`

## Context

The SSRF scanner already exists at `packages/cherenkov/scanners/ssrf_scanner.py`.
This task is to **verify** it fully follows the `BaseScanner` contract and fix any
deviations. Also ensure it has proper tests.

## Context files

```
packages/cherenkov/scanners/ssrf_scanner.py    ← existing — VERIFY
packages/cherenkov/core/base_scanner.py        ← contract
```

## What to do

1. **Read the existing scanner** and verify against checklist:
   - [ ] Inherits `BaseScanner`
   - [ ] Constructor calls `super().__init__(name="ssrf", description="...")`
   - [ ] Implements `async def scan(self, target: str, timeout: float = 10.0) -> ScanResult`
   - [ ] Returns `ScanResult` with correct `scanner_name` field
   - [ ] Uses `self._http_request()` for HTTP calls (not raw `requests`)
   - [ ] All findings use `Finding` dataclass with proper `Severity`
   - [ ] No outbound calls beyond `target` (MEISSNER) — **critical for SSRF scanner**
   - [ ] SSRF payloads target ONLY the scan target, never external services
   - [ ] No bare `os.remove()` (Shred invariant)
   - [ ] Passes `ruff format` and `ruff check`

2. **Fix any deviations** found above

3. **MEISSNER audit** — extra scrutiny for SSRF scanner:
   - Verify that SSRF test payloads (e.g., `http://169.254.169.254/`) are sent
     TO the target's input fields, not as actual outbound requests
   - Ensure no callback servers or external canary URLs are used

4. **Ensure unit test exists** at `tests/unit/test_ssrf_scanner.py`:
   ```python
   import pytest
   from cherenkov.scanners.ssrf_scanner import SsrfScanner  # or SSRFScanner

   @pytest.mark.asyncio
   async def test_ssrf_scanner_returns_scan_result():
       scanner = SsrfScanner()
       assert scanner.name == "ssrf"
       result = await scanner.scan("http://target.example.com")
       assert result.scanner_name == "ssrf"
       assert isinstance(result.findings, list)
   ```

## Files to modify

- `packages/cherenkov/scanners/ssrf_scanner.py` — fix if needed
- `tests/unit/test_ssrf_scanner.py` — create or update

## Verify

```bash
ruff format packages/ && ruff check packages/ --ignore W,S,B
pytest tests/unit/test_ssrf_scanner.py -v
python -c "from cherenkov.scanners.ssrf_scanner import *; import inspect; [print(name) for name, obj in locals().items() if inspect.isclass(obj)]"
```
