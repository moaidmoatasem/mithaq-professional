# Task: Issue #237 — Scan result aggregation pipeline

**Branch:** `feat/237-aggregator`
**Labels:** `priority:high, feature, phase-2, area:scanner`
**Milestone:** v1.1.0
**PR must contain:** `Closes #237`

## Context

When N scanners run in parallel against the same target, their results need to be
merged and deduplicated before returning to the caller. This module merges `ScanResult`
objects, deduplicates findings, and produces a unified report.

## Context files

```
packages/cherenkov/core/base_scanner.py    ← ScanResult, Finding dataclasses
packages/cherenkov/core/registry.py        ← provides list of scanners
packages/cherenkov/core/aggregator.py      ← NEW — create this
```

## What to do

1. **Create `packages/cherenkov/core/aggregator.py`**:

   ```python
   """Scan result aggregation pipeline — merges findings from N parallel scanners."""
   from __future__ import annotations

   import asyncio
   import time
   from dataclasses import dataclass, field
   from cherenkov.core.base_scanner import BaseScanner, ScanResult, Finding

   @dataclass
   class AggregatedResult:
       target: str
       findings: list[Finding] = field(default_factory=list)
       scanner_names: list[str] = field(default_factory=list)
       total_duration_ms: float = 0.0
       deduplicated_count: int = 0

   def _dedup_key(f: Finding) -> tuple:
       """Deduplication key: (target context, scanner, finding type, location)."""
       return (
           getattr(f, "target", ""),
           getattr(f, "scanner_name", ""),
           getattr(f, "finding_type", getattr(f, "title", "")),
           getattr(f, "location", getattr(f, "url", "")),
       )

   def deduplicate_findings(findings: list[Finding]) -> list[Finding]:
       """Remove duplicate findings by composite key."""
       seen: set[tuple] = set()
       unique: list[Finding] = []
       for f in findings:
           key = _dedup_key(f)
           if key not in seen:
               seen.add(key)
               unique.append(f)
       return unique

   async def aggregate_scans(
       scanners: list[BaseScanner],
       target: str,
       timeout: float = 30.0,
   ) -> AggregatedResult:
       """Run all scanners concurrently, merge and deduplicate results."""
       start = time.monotonic()

       tasks = [scanner.scan(target, timeout=timeout) for scanner in scanners]
       results: list[ScanResult] = await asyncio.gather(*tasks, return_exceptions=True)

       all_findings: list[Finding] = []
       scanner_names: list[str] = []

       for result in results:
           if isinstance(result, Exception):
               continue  # Skip failed scanners
           all_findings.extend(result.findings)
           scanner_names.append(result.scanner_name)

       raw_count = len(all_findings)
       deduped = deduplicate_findings(all_findings)

       return AggregatedResult(
           target=target,
           findings=deduped,
           scanner_names=scanner_names,
           total_duration_ms=(time.monotonic() - start) * 1000,
           deduplicated_count=raw_count - len(deduped),
       )
   ```

2. **Write tests**:
   ```python
   # tests/unit/test_aggregator.py
   import pytest
   from cherenkov.core.aggregator import deduplicate_findings, aggregate_scans

   def test_deduplicate_removes_exact_dupes():
       ...

   @pytest.mark.asyncio
   async def test_aggregate_scans_runs_all_scanners():
       ...

   @pytest.mark.asyncio
   async def test_aggregate_scans_handles_failures():
       ...
   ```

## Files to modify

- `packages/cherenkov/core/aggregator.py` — NEW
- `tests/unit/test_aggregator.py` — NEW

## Verify

```bash
ruff format packages/ && ruff check packages/ --ignore W,S,B
pytest tests/unit/test_aggregator.py -v
```
