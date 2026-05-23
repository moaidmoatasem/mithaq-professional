# Task: Issue #240 — Graduate NetworkVulnerabilityScanner

**Branch:** `feat/240-network-scanner`
**Labels:** `priority:high, feature, phase-3, area:scanner`
**Milestone:** v1.5.0
**PR must contain:** `Closes #240`

## Context

Graduate the autonomous-generated `NetworkVulnerabilityScanner` from raw AI output
to a production-ready scanner that follows the `BaseScanner` contract.

## Context files

```
packages/cherenkov/autonomous_generated/scanners/networkvulnerabilityscanner.py  ← SOURCE
packages/cherenkov/scanners/network_vulnerability_scanner.py                     ← DEST (new)
packages/cherenkov/core/base_scanner.py                                          ← contract
```

## What to do

1. **Read the source** file and understand its detection logic

2. **Create the graduated scanner** at `packages/cherenkov/scanners/network_vulnerability_scanner.py`:

   ```python
   """Network Vulnerability Scanner — detects open ports, exposed services, and network misconfigs."""
   from __future__ import annotations

   import time
   from cherenkov.core.base_scanner import BaseScanner, ScanResult, Finding, Severity

   class NetworkVulnerabilityScanner(BaseScanner):
       def __init__(self):
           super().__init__(
               name="network_vulnerability",
               description="Scans for open ports, exposed services, and network-level vulnerabilities",
           )

       async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
           start = time.monotonic()
           findings: list[Finding] = []

           # Port/service detection logic adapted from source
           # Use self._http_request(target, timeout) for HTTP probes
           # MUST NOT make outbound calls beyond the target (MEISSNER)

           return ScanResult(
               target=target,
               scanner_name=self.name,
               findings=findings,
               duration_ms=(time.monotonic() - start) * 1000,
           )
   ```

3. **Checklist for graduation**:
   - [ ] Inherits `BaseScanner`
   - [ ] Implements `async def scan(self, target: str, timeout: float) -> ScanResult`
   - [ ] Uses `self._http_request()` for HTTP calls (not raw `requests` or `aiohttp`)
   - [ ] All findings use `Finding` dataclass with proper `Severity`
   - [ ] No outbound calls beyond `target` (MEISSNER)
   - [ ] No bare `os.remove()` (Shred invariant)
   - [ ] Passes `ruff format` and `ruff check`

4. **Write unit test**:
   ```python
   # tests/unit/test_network_vulnerability_scanner.py
   import pytest
   from unittest.mock import AsyncMock, patch
   from cherenkov.scanners.network_vulnerability_scanner import NetworkVulnerabilityScanner

   @pytest.mark.asyncio
   async def test_network_scanner_returns_scan_result():
       scanner = NetworkVulnerabilityScanner()
       result = await scanner.scan("http://target.example.com")
       assert result.scanner_name == "network_vulnerability"
       assert result.target == "http://target.example.com"
       assert isinstance(result.findings, list)
       assert result.duration_ms >= 0
   ```

## Files to modify

- `packages/cherenkov/scanners/network_vulnerability_scanner.py` — NEW
- `tests/unit/test_network_vulnerability_scanner.py` — NEW

## Verify

```bash
ruff format packages/ && ruff check packages/ --ignore W,S,B
pytest tests/unit/test_network_vulnerability_scanner.py -v
python -c "from cherenkov.scanners.network_vulnerability_scanner import NetworkVulnerabilityScanner; s = NetworkVulnerabilityScanner(); print(f'{s.name}: {s.description}')"
```
