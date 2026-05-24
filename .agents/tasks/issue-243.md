# Task: Issue #243 — Graduate CI/CD Integration Scanner

**Branch:** `feat/243-cicd-scanner`
**Labels:** `priority:medium, feature, phase-3, area:scanner`
**Milestone:** v1.5.0
**PR must contain:** `Closes #243`

## Context

Graduate the autonomous-generated `CICDIntegrationScanner` from raw AI output to a
production-ready scanner following the `BaseScanner` contract. This scanner detects
CI/CD pipeline misconfigurations and exposed build artifacts.

## Context files

```
packages/cherenkov/autonomous_generated/scanners/cicdintegrationscanner.py  ← SOURCE
packages/cherenkov/scanners/cicd_integration_scanner.py                     ← DEST (new)
packages/cherenkov/core/base_scanner.py                                     ← contract
```

## What to do

1. **Read the source** file and understand its detection logic

2. **Create the graduated scanner** at `packages/cherenkov/scanners/cicd_integration_scanner.py`:

   ```python
   """CI/CD Integration Scanner — detects pipeline misconfigs and exposed build artifacts."""
   from __future__ import annotations

   import time
   from cherenkov.core.base_scanner import BaseScanner, ScanResult, Finding, Severity

   class CICDIntegrationScanner(BaseScanner):
       def __init__(self):
           super().__init__(
               name="cicd_integration",
               description="Scans for CI/CD pipeline misconfigurations and exposed build artifacts",
           )

       async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
           start = time.monotonic()
           findings: list[Finding] = []

           # Check for exposed CI paths: /.github/, /Jenkinsfile, /.gitlab-ci.yml,
           # /bitbucket-pipelines.yml, /.circleci/, /.travis.yml
           # Check for exposed build artifacts, env files, docker-compose
           # Use self._http_request(target, timeout)

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
   - [ ] No outbound calls beyond `target` (MEISSNER)
   - [ ] No bare `os.remove()` (Shred invariant)
   - [ ] Passes `ruff format` and `ruff check`

4. **Write unit test** at `tests/unit/test_cicd_integration_scanner.py`:
   ```python
   import pytest
   from cherenkov.scanners.cicd_integration_scanner import CICDIntegrationScanner

   @pytest.mark.asyncio
   async def test_cicd_scanner_returns_scan_result():
       scanner = CICDIntegrationScanner()
       assert scanner.name == "cicd_integration"
       result = await scanner.scan("http://target.example.com")
       assert result.scanner_name == "cicd_integration"
       assert isinstance(result.findings, list)
   ```

## Files to modify

- `packages/cherenkov/scanners/cicd_integration_scanner.py` — NEW
- `tests/unit/test_cicd_integration_scanner.py` — NEW

## Verify

```bash
ruff format packages/ && ruff check packages/ --ignore W,S,B
pytest tests/unit/test_cicd_integration_scanner.py -v
python -c "from cherenkov.scanners.cicd_integration_scanner import CICDIntegrationScanner; s = CICDIntegrationScanner(); print(f'{s.name}: {s.description}')"
```
