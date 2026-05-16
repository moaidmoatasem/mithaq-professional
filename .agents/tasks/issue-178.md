# Task: Issue #178 — Graduate autonomous scanners to BaseScanner

**Branch:** `feat/178-graduate-scanners`
**Labels:** `feature, phase-2, area:scanner, priority:medium, ai:generated`
**PR must contain:** `Closes #178`

## Context files

```
packages/cherenkov/core/base_scanner.py              ← contract to implement
packages/cherenkov/core/registry.py                  ← ScannerRegistry.register()
packages/cherenkov/autonomous_generated/scanners/    ← source candidates
packages/cherenkov/scanners/                         ← destination
```

## Candidates (pick any 3–5)

| File | What it detects |
|---|---|
| `xxe_scanner.py` | XML External Entity injection |
| `pathtraversalscanner.py` | Path traversal / LFI |
| `fileuploadscanner.py` | Unsafe file upload |
| `networkvulnerabilityscanner.py` | Open ports / network exposure |
| `cicdintegrationscanner.py` | CI/CD pipeline misconfig |

## For each scanner — pattern to follow

```python
# packages/cherenkov/scanners/<name>.py
from cherenkov.core.base_scanner import BaseScanner, ScanResult, Finding, Severity

class XxeScanner(BaseScanner):
    def __init__(self):
        super().__init__(name="xxe", description="XML External Entity injection scanner")

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        import time
        start = time.monotonic()
        findings = []
        # ... detection logic using self._http_request(target, timeout) ...
        return ScanResult(
            target=target,
            scanner_name=self.name,
            findings=findings,
            duration_ms=(time.monotonic() - start) * 1000,
        )
```

Register in `packages/cherenkov/core/registry.py`:
```python
from cherenkov.scanners.xxe_scanner import XxeScanner
registry.register(XxeScanner())
```

## Test pattern

```python
# tests/unit/test_xxe_scanner.py
import pytest
from unittest.mock import AsyncMock, patch
from cherenkov.scanners.xxe_scanner import XxeScanner

@pytest.mark.asyncio
async def test_xxe_scanner_returns_result():
    scanner = XxeScanner()
    with patch.object(scanner, '_http_request', new_callable=AsyncMock) as mock_req:
        mock_req.return_value.text = '<?xml version="1.0"?>'
        mock_req.return_value.status_code = 200
        result = await scanner.scan("http://target.example.com")
    assert result.scanner_name == "xxe"
    assert result.target == "http://target.example.com"
```

## Verify

```bash
ruff format packages/ && ruff check packages/ --ignore W,S,B
pytest tests/unit/test_*scanner* -v
```
