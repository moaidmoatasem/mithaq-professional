# CHERENKOV — Shared Agent Context

> Every agent reads this first. It is the single source of truth for project rules.
> For tool-specific config: CLAUDE.md (Claude), GEMINI.md (Jules), .continue/config.yaml, opencode.jsonc

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
    tokamak.py         ← Execution sandbox (223-line stub — Sprint 3)
    storage/database.py← SQLite WAL helpers: init_db, save_scan
  scanners/            ← Production scanners (registered in registry.py)
  orchestration/       ← Workflow engine, agent factory
  compliance/          ← (to be created — Sprint 5)
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

## Active Issues → task files

**P0 — Pick these first. Phase 2 is blocked until they are done.**

| Issue | File | Priority |
|---|---|---|
| [#222](https://github.com/moaidmoatasem/cherenkov-professional/issues/222) | `.agents/tasks/issue-222.md` | 🔴 P0 — TOKAMAK Docker sandbox |
| [#221](https://github.com/moaidmoatasem/cherenkov-professional/issues/221) | `.agents/tasks/issue-221.md` | 🔴 P0 — Real health metrics |
| [#224](https://github.com/moaidmoatasem/cherenkov-professional/issues/224) | `.agents/tasks/issue-224.md` | 🔴 P0 — LATTICE Qdrant wiring |
| [#223](https://github.com/moaidmoatasem/cherenkov-professional/issues/223) | `.agents/tasks/issue-223.md` | 🔴 P0 — Root cleanup |

**Phase 2 remaining (after P0):**

| Issue | File | Priority |
|---|---|---|
| [#177](https://github.com/moaidmoatasem/cherenkov-professional/issues/177) | `.agents/tasks/issue-177.md` | P1 — SQLite persistence |
| [#178](https://github.com/moaidmoatasem/cherenkov-professional/issues/178) | `.agents/tasks/issue-178.md` | P1 — Scanner graduation |

**Do NOT pick up Phase 3/4 issues (#183–#190) until Phase 2 P0 items above are closed.**

## How to pick up a task

1. Read `.agents/context.md` (this file)
2. Read `.agents/tasks/issue-<N>.md`
3. `git checkout -b feat/<N>-<slug>`
4. Implement, run verify commands from task file
5. `gh pr create` with `Closes #<N>` in body
