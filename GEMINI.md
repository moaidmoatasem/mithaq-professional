# CHERENKOV — Gemini Agent Configuration (Jules + Antigravity)

> This file configures all Gemini-powered agents.
> **Jules** = backend/Python domain. **Antigravity** = frontend TypeScript/React domain.
> For Claude agents, see CLAUDE.md. Both files share the same architectural rules.

---

## Agent Roster & Domain Ownership

| Agent | Trigger | Primary Domain | Branch Prefix |
|---|---|---|---|
| **Antigravity (Google IDE)** | Gravity preview, local dev | `packages/cherenkov/web/` frontend | `feat/web-*` |
| **Claude (GitHub Actions)** | `@claude` in issues/PRs | Code review, targeted fixes, issue work | `claude/*` |
| **Claude Code (local)** | Terminal sessions | Architecture, agentic coordination, multi-file refactors | `claude/*` |
| **Autonomous Pipeline** | Daily cron 2AM UTC | Scanner generation (`autonomous_roadmap_executor.py`) | `auto-dev/<run>` |
| **Security Architect** | Scan initiation | Threat modeling, EngagementPlan, LATTICE queries | `feat/arch-*` |
| **Red Team Agent** | EngagementPlan start | Active exploitation, CVE mapping, TOKAMAK validation | `feat/red-*` |
| **SecOps Agent** | Scan completion | Compliance mapping, EGY-FIN CSF reports | `feat/secops-*` |

---

## Antigravity — Frontend Agent

**Domain (strict):** `packages/cherenkov/web/src/` only. Never touch Python or `packages/cherenkov/api/`.

### Environment
- Vite dev server: port `3000`
- Proxies to FastAPI backend: port `8000` (configured in `vite.config.ts`)
- Never hard-code `localhost:8000` — use `API_BASE` and `getWsUrl()` from `@/src/lib/api.ts`

### Import pattern
```typescript
import { API_BASE } from '@/src/lib/api';
import { useMetrics } from '@/src/hooks/useMetrics';
import { ForensicHeader } from '@/src/components/organisms/ForensicHeader';
```

### Pre-commit
```bash
cd packages/cherenkov/web
npm run lint        # tsc --noEmit
npx vite build      # production build must pass
```

### Branching
- Branch prefix: `feat/web-<issue>-<slug>`
- PR body must contain `Closes #<N>`

---

## Jules — Backend / Scanner Agent

## Environment

```
Python : 3.11 (CI) / 3.10+ (local)
Node   : 20+ (frontend only)
OS     : Ubuntu (CI) / Windows WSL2 (local dev)
```

### Setup
```bash
pip install -e ".[dev]"
```

### Test
```bash
pytest -m "not (integration or ai_generated)" --tb=short
```

### Lint + Format (Python)
```bash
ruff format packages/
ruff check packages/ --ignore W,S,B
```

### Lint + Build (Frontend)
```bash
cd packages/cherenkov/web
npm install
npm run lint        # tsc --noEmit
npx vite build
```

## Repo Layout

```
packages/cherenkov/
  api/          FastAPI server  (main.py — all /api/v1/* routes)
  core/         Domain logic    (base_scanner, circuit_breaker, tokamak, …)
  scanners/     Production-ready scanners (inherit BaseScanner)
  orchestration/Workflow engine (architect, red_team, secops, etc.)
  web/src/      React 19 + Vite + Tailwind v4 dashboard
  autonomous_generated/  Raw AI output — do not import directly

tests/          pytest suite (unit + integration markers)
scripts/        Autonomous pipeline scripts
.github/        CI workflows + Claude/Jules actions
```

## Architectural Invariants (Non-Negotiable)

1. **Zero-egress (MEISSNER):** No outbound calls outside the scan target. All LLM calls go through local Ollama or gated Groq. Never add `requests.get(<external_url>)` in core logic.
2. **ABLATION:** Any payload sent to an LLM API must pass through `cherenkov.core.ablation` to redact PII/secrets.
3. **TOKAMAK signing:** Every PoC execution result must carry `trace_hash = sha256(output + timestamp)`.
4. **Shred receipts:** Temp file cleanup = cryptographic overwrite + JSON receipt. No bare `os.remove()`.

## Import Convention

```python
# Correct
from cherenkov.core.base_scanner import BaseScanner, ScanResult, Finding, Severity
from cherenkov.core.circuit_breaker import CircuitBreaker

# Wrong — do not use
from src.cherenkov.X import Y
```

## Branching

- Branch: `feat/<issue-number>-<slug>` | `fix/<issue-number>-<slug>`
- PR base: `main`
- Reference issue: body must contain `Closes #<N>`
- Never push to `main` directly

## Key GitHub Issues (active work)

| # | What | Priority | Phase |
|---|---|---|---|
| [#230](https://github.com/moaidmoatasem/cherenkov-professional/issues/230) | Remove cloud configs (MEISSNER) | critical | Phase 2 |
| [#234](https://github.com/moaidmoatasem/cherenkov-professional/issues/234) | Harden .gitignore | high | Phase 2 |
| [#236](https://github.com/moaidmoatasem/cherenkov-professional/issues/236) | Scanner registry auto-discovery | high | Phase 2 |
| [#237](https://github.com/moaidmoatasem/cherenkov-professional/issues/237) | Scan result aggregation pipeline | high | Phase 2 |
| [#238](https://github.com/moaidmoatasem/cherenkov-professional/issues/238) | Wire POST /api/v1/scan (depends #236, #237) | high | Phase 2 |
| [#239](https://github.com/moaidmoatasem/cherenkov-professional/issues/239) | CI matrix 146+ tests pass | high | Phase 2 |
| [#233](https://github.com/moaidmoatasem/cherenkov-professional/issues/233) | Align GEMINI.md with AGENTS.md roster | medium | Phase 2 |
| [#246](https://github.com/moaidmoatasem/cherenkov-professional/issues/246) | TOKAMAK SQLite WAL logger | critical | Phase 3 |
| [#247](https://github.com/moaidmoatasem/cherenkov-professional/issues/247) | Wire Cherenkov Trace signing | critical | Phase 3 |

