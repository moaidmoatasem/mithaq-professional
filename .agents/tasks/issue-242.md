# Task: Issue #242 — Graduate CVE Database Scanner

**Branch:** `feat/242-cve-scanner`
**Labels:** `priority:medium, feature, phase-3, area:scanner`
**Milestone:** v1.5.0
**PR must contain:** `Closes #242`

## Context

Graduate the autonomous-generated `CVEDatabaseScanner` from raw AI output to a
production-ready scanner following the `BaseScanner` contract. This scanner checks
discovered technologies against known CVE databases.

## Context files

```
packages/cherenkov/autonomous_generated/scanners/cvedatabasescanner.py  ← SOURCE
packages/cherenkov/scanners/cve_database_scanner.py                     ← DEST (new)
packages/cherenkov/core/base_scanner.py                                 ← contract
```

## What to do

1. **Read the source** file and understand its detection logic

2. **Create the graduated scanner** at `packages/cherenkov/scanners/cve_database_scanner.py`:

   ```python
   """CVE Database Scanner — checks target technologies against known vulnerabilities."""
   from __future__ import annotations

   import time
   from cherenkov.core.base_scanner import BaseScanner, ScanResult, Finding, Severity

   class CVEDatabaseScanner(BaseScanner):
       def __init__(self):
           super().__init__(
               name="cve_database",
               description="Checks detected technologies and versions against known CVE databases",
           )

       async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
           start = time.monotonic()
           findings: list[Finding] = []

           # Technology fingerprinting + CVE matching logic from source
           # Use self._http_request(target, timeout) for HTTP probes
           # CVE data MUST be bundled locally — no external API calls (MEISSNER)

           return ScanResult(
               target=target,
               scanner_name=self.name,
               findings=findings,
               duration_ms=(time.monotonic() - start) * 1000,
           )
   ```

3. **Graduation checklist**:
   - [ ] Inherits `BaseScanner`
   - [ ] Implements `async def scan(self, target: str, timeout: float) -> ScanResult`
   - [ ] Uses `self._http_request()` for HTTP calls
   - [ ] All findings use `Finding` dataclass with proper `Severity`
   - [ ] CVE data is local/bundled — no external API calls (MEISSNER)
   - [ ] No bare `os.remove()` (Shred invariant)
   - [ ] Passes `ruff format` and `ruff check`

4. **Write unit test** at `tests/unit/test_cve_database_scanner.py`:
   ```python
   import pytest
   from cherenkov.scanners.cve_database_scanner import CVEDatabaseScanner

   @pytest.mark.asyncio
   async def test_cve_scanner_returns_scan_result():
       scanner = CVEDatabaseScanner()
       assert scanner.name == "cve_database"
       result = await scanner.scan("http://target.example.com")
       assert result.scanner_name == "cve_database"
       assert isinstance(result.findings, list)
   ```

## Files to modify

- `packages/cherenkov/scanners/cve_database_scanner.py` — NEW
- `tests/unit/test_cve_database_scanner.py` — NEW

## Verify

```bash
ruff format packages/ && ruff check packages/ --ignore W,S,B
pytest tests/unit/test_cve_database_scanner.py -v
python -c "from cherenkov.scanners.cve_database_scanner import CVEDatabaseScanner; s = CVEDatabaseScanner(); print(f'{s.name}: {s.description}')"
```
