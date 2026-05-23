# CHERENKOV — Shared Agent Context

> Every agent reads this first. It is the single source of truth for project rules.
> For tool-specific config: CLAUDE.md (Claude), GEMINI.md (Jules + Antigravity), opencode.jsonc

## Quick Reference

| Thing | Value |
|---|---|
| Python | 3.11 (CI) / 3.10+ |
| Install | `pip install -e ".[dev]"` |
| Test | `pytest -m "not (integration or ai_generated)" --tb=short` |
| Lint/fmt | `ruff format packages/ && ruff check packages/ --ignore W,S,B` |
| Frontend | `cd packages/cherenkov/web && npm run lint && npx vite build` |
| Branch | `feat/<issue>-<slug>` or `fix/<issue>-<slug>` |
| PR body | Must contain `Closes #<N>` |

## Repo Map

```
packages/cherenkov/
  api/main.py          ← FastAPI: /api/v1/* routes, /ws/live WebSocket
  core/
    base_scanner.py    ← BaseScanner, ScanResult, Finding, Severity (START HERE)
    circuit_breaker.py ← CircuitBreaker, Meissner, meissner_hub
    registry.py        ← ScannerRegistry — auto-discover BaseScanner subclasses (#236)
    aggregator.py      ← Scan result aggregation pipeline (#237)
    tokamak.py         ← Execution sandbox (TOKAMAK signing)
    storage/database.py← SQLite WAL helpers: init_db, save_trace, compute_trace_hash
  scanners/            ← Production scanners (auto-discovered by registry)
  orchestration/       ← Workflow engine, agent factory, architect, red_team, secops
  compliance/          ← (to be created — Phase 5)

  web/src/
    lib/api.ts         ← API_BASE, getWsUrl(), typed interfaces, fetch helpers
    hooks/             ← useMetrics, useLiveEvents
    components/        ← atoms / molecules / organisms / templates

tests/                 ← pytest suite (unit + integration markers)
.agents/tasks/         ← One task file per GitHub issue (this directory)
```

## Invariants (never break these)

1. **MEISSNER** — zero outbound calls beyond the scan target URL
2. **ABLATION** — pipe LLM payloads through `cherenkov.core.ablation` before sending
3. **TOKAMAK** — all PoC output must be SHA-256 signed (`trace_hash`)
4. **Shred** — temp file cleanup = overwrite + JSON receipt, never bare `os.remove()`

## Import rules

```python
# Always
from cherenkov.core.base_scanner import BaseScanner, ScanResult, Finding, Severity

# Never
from src.cherenkov.X import Y
```

```typescript
// Always — use relative alias, never hardcode port
import { API_BASE, getWsUrl } from '@/src/lib/api';

// Never
const url = 'http://localhost:8000/api/v1/...'
```

---

## Active Issues → task files

> Last updated: 2026-05-23. Issues #174–#224 are **closed** (see `.agents/tasks/archive/README.md`).

### 🔴 v1.1.0 — Phase 2 (Sprint 2, current)

**P0 — Pick these first. Phase 2 is blocked until they are done.**

| Issue | File | Priority | Type |
|---|---|---|---|
| [#230](https://github.com/moaidmoatasem/cherenkov-professional/issues/230) | `issue-230.md` | 🔴 critical | security — remove cloud configs (MEISSNER) |
| [#234](https://github.com/moaidmoatasem/cherenkov-professional/issues/234) | `issue-234.md` | 🟠 high | chore — harden .gitignore |
| [#236](https://github.com/moaidmoatasem/cherenkov-professional/issues/236) | `issue-236.md` | 🟠 high | feat — scanner registry auto-discovery |
| [#237](https://github.com/moaidmoatasem/cherenkov-professional/issues/237) | `issue-237.md` | 🟠 high | feat — scan result aggregation pipeline |
| [#238](https://github.com/moaidmoatasem/cherenkov-professional/issues/238) | `issue-238.md` | 🟠 high | feat — wire POST /api/v1/scan (depends #236, #237) |
| [#239](https://github.com/moaidmoatasem/cherenkov-professional/issues/239) | `issue-239.md` | 🟠 high | test — CI matrix 146+ tests pass |

**P1 — Phase 2 remaining (after P0):**

| Issue | File | Priority | Type |
|---|---|---|---|
| [#231](https://github.com/moaidmoatasem/cherenkov-professional/issues/231) | `issue-231.md` | 🟡 medium | chore — GitHub repo metadata |
| [#232](https://github.com/moaidmoatasem/cherenkov-professional/issues/232) | `issue-232.md` | 🟡 medium | chore — root cleanup (in-progress) |
| [#233](https://github.com/moaidmoatasem/cherenkov-professional/issues/233) | `issue-233.md` | 🟡 medium | chore — align GEMINI.md |
| [#235](https://github.com/moaidmoatasem/cherenkov-professional/issues/235) | `issue-235.md` | 🔵 low | chore — canonicalize CHANGELOG |

### 🟣 v1.5.0 — Phase 3 (Scanner Graduation)

**Do NOT start Phase 3 until all Phase 2 P0 items above are closed.**

**P0 — Critical infrastructure:**

| Issue | File | Priority | Type |
|---|---|---|---|
| [#246](https://github.com/moaidmoatasem/cherenkov-professional/issues/246) | `issue-246.md` | 🔴 critical | feat — TOKAMAK SQLite WAL logger |
| [#247](https://github.com/moaidmoatasem/cherenkov-professional/issues/247) | `issue-247.md` | 🔴 critical | feat — wire Cherenkov Trace signing (depends #237, #246) |

**P1 — Scanner graduation (high priority):**

| Issue | File | Priority | Type |
|---|---|---|---|
| [#240](https://github.com/moaidmoatasem/cherenkov-professional/issues/240) | `issue-240.md` | 🟠 high | feat — graduate NetworkVulnerabilityScanner |
| [#241](https://github.com/moaidmoatasem/cherenkov-professional/issues/241) | `issue-241.md` | 🟠 high | feat — verify XXE scanner contract |
| [#245](https://github.com/moaidmoatasem/cherenkov-professional/issues/245) | `issue-245.md` | 🟠 high | feat — verify SSRF scanner contract |

**P2 — Scanner graduation (medium priority):**

| Issue | File | Priority | Type |
|---|---|---|---|
| [#242](https://github.com/moaidmoatasem/cherenkov-professional/issues/242) | `issue-242.md` | 🟡 medium | feat — graduate CVE Database Scanner |
| [#243](https://github.com/moaidmoatasem/cherenkov-professional/issues/243) | `issue-243.md` | 🟡 medium | feat — graduate CI/CD Integration Scanner |
| [#244](https://github.com/moaidmoatasem/cherenkov-professional/issues/244) | `issue-244.md` | 🟡 medium | feat — graduate AttackChainDetector |

---

## Dependency Graph

```
Phase 2 (v1.1.0):
  #230 (MEISSNER cleanup) ── no deps, do first
  #234 (.gitignore) ── no deps
  #236 (registry) ── no deps
  #237 (aggregator) ── no deps
  #238 (scan endpoint) ── depends on #236 + #237
  #239 (CI tests) ── do last in Phase 2, verifies everything

Phase 3 (v1.5.0):
  #246 (SQLite WAL) ── no deps
  #247 (trace signing) ── depends on #237 + #246
  #240–#245 (scanner graduation) ── independent of each other
```


## How to pick up a task

1. Read `.agents/context.md` (this file)
2. Read `.agents/tasks/issue-<N>.md`
3. `git checkout -b feat/<N>-<slug>`
4. Implement, run verify commands from task file
5. `gh pr create` with `Closes #<N>` in body
