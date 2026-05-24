# Task: Issue #244 — Graduate AttackChainDetector

**Branch:** `feat/244-attack-chain`
**Labels:** `priority:medium, feature, phase-3, area:scanner`
**Milestone:** v1.5.0
**PR must contain:** `Closes #244`

## Context

Graduate the autonomous-generated `AttackChainDetector` from raw AI output to a
production-ready scanner following the `BaseScanner` contract. This scanner correlates
individual vulnerability findings into multi-step attack chains.

## Context files

```
packages/cherenkov/autonomous_generated/scanners/attackchaindetector.py  ← SOURCE
packages/cherenkov/scanners/attack_chain_detector.py                     ← DEST (new)
packages/cherenkov/core/base_scanner.py                                  ← contract
```

## What to do

1. **Read the source** file and understand its detection/correlation logic

2. **Create the graduated scanner** at `packages/cherenkov/scanners/attack_chain_detector.py`:

   ```python
   """Attack Chain Detector — correlates findings into multi-step attack chains."""
   from __future__ import annotations

   import time
   from cherenkov.core.base_scanner import BaseScanner, ScanResult, Finding, Severity

   class AttackChainDetector(BaseScanner):
       def __init__(self):
           super().__init__(
               name="attack_chain",
               description="Correlates individual findings into multi-step attack chains",
           )

       async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
           start = time.monotonic()
           findings: list[Finding] = []

           # Attack chain correlation logic:
           # 1. Gather individual vulnerability signals from target
           # 2. Correlate signals into potential attack chains
           # 3. Score chain severity based on combined impact
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

4. **Write unit test** at `tests/unit/test_attack_chain_detector.py`:
   ```python
   import pytest
   from cherenkov.scanners.attack_chain_detector import AttackChainDetector

   @pytest.mark.asyncio
   async def test_attack_chain_returns_scan_result():
       scanner = AttackChainDetector()
       assert scanner.name == "attack_chain"
       result = await scanner.scan("http://target.example.com")
       assert result.scanner_name == "attack_chain"
       assert isinstance(result.findings, list)
   ```

## Files to modify

- `packages/cherenkov/scanners/attack_chain_detector.py` — NEW
- `tests/unit/test_attack_chain_detector.py` — NEW

## Verify

```bash
ruff format packages/ && ruff check packages/ --ignore W,S,B
pytest tests/unit/test_attack_chain_detector.py -v
python -c "from cherenkov.scanners.attack_chain_detector import AttackChainDetector; s = AttackChainDetector(); print(f'{s.name}: {s.description}')"
```
