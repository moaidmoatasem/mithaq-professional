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

| Issue | File | Status |
|---|---|---|
| [#174](https://github.com/moaidmoatasem/cherenkov-professional/issues/174) | `.agents/tasks/issue-174.md` | open |
| [#175](https://github.com/moaidmoatasem/cherenkov-professional/issues/175) | `.agents/tasks/issue-175.md` | open |
| [#176](https://github.com/moaidmoatasem/cherenkov-professional/issues/176) | `.agents/tasks/issue-176.md` | open |
| [#177](https://github.com/moaidmoatasem/cherenkov-professional/issues/177) | `.agents/tasks/issue-177.md` | open |
| [#178](https://github.com/moaidmoatasem/cherenkov-professional/issues/178) | `.agents/tasks/issue-178.md` | open |

## How to pick up a task

1. Read `.agents/context.md` (this file)
2. Read `.agents/tasks/issue-<N>.md`
3. `git checkout -b feat/<N>-<slug>`
4. Implement, run verify commands from task file
5. `gh pr create` with `Closes #<N>` in body
