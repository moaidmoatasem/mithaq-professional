# Task: Issue #241 — Graduate/verify XXE Scanner

**Branch:** `feat/241-xxe-verify`
**Labels:** `priority:high, feature, phase-3, area:scanner`
**Milestone:** v1.5.0
**PR must contain:** `Closes #241`

## Context

The XXE scanner already exists at `packages/cherenkov/scanners/xxe_scanner.py`.
This task is to **verify** it fully follows the `BaseScanner` contract and fix any
deviations. Also ensure it has proper tests.

## Context files

```
packages/cherenkov/scanners/xxe_scanner.py     ← existing — VERIFY
packages/cherenkov/core/base_scanner.py        ← contract
packages/cherenkov/autonomous_generated/scanners/xxe_scanner.py  ← original source
```

## What to do

1. **Read the existing scanner** and verify against checklist:
   - [ ] Inherits `BaseScanner`
   - [ ] Constructor calls `super().__init__(name="xxe", description="...")`
   - [ ] Implements `async def scan(self, target: str, timeout: float = 10.0) -> ScanResult`
   - [ ] Returns `ScanResult` with correct `scanner_name` field
   - [ ] Uses `self._http_request()` for HTTP calls (not raw `requests`)
   - [ ] All findings use `Finding` dataclass with proper `Severity`
   - [ ] No outbound calls beyond `target` (MEISSNER)
   - [ ] No bare `os.remove()` (Shred invariant)
   - [ ] Passes `ruff format` and `ruff check`

2. **Fix any deviations** found above

3. **Ensure unit test exists** at `tests/unit/test_xxe_scanner.py`:
   ```python
   import pytest
   from cherenkov.scanners.xxe_scanner import XxeScanner

   @pytest.mark.asyncio
   async def test_xxe_scanner_returns_scan_result():
       scanner = XxeScanner()
       assert scanner.name == "xxe"
       result = await scanner.scan("http://target.example.com")
       assert result.scanner_name == "xxe"
       assert isinstance(result.findings, list)
   ```

4. **Register in registry** (if not auto-discovered via #236)

## Files to modify

- `packages/cherenkov/scanners/xxe_scanner.py` — fix if needed
- `tests/unit/test_xxe_scanner.py` — create or update

## Verify

```bash
ruff format packages/ && ruff check packages/ --ignore W,S,B
pytest tests/unit/test_xxe_scanner.py -v
python -c "from cherenkov.scanners.xxe_scanner import XxeScanner; s = XxeScanner(); print(f'{s.name}: {s.description}')"
```
