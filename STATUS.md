# CHERENKOV Project Status

## Build Health
| Check | Status |
|---|---|
| Tests | ✅ 68 passed, 7 skipped (integration correctly gated) |
| Ruff lint | ✅ Passing |
| Ruff format | ✅ Passing |
| TypeScript (web) | ✅ Zero errors |
| Vite build | ✅ Clean (414 kB JS, 54 kB CSS) |

## Current Phase: Phase 2 — Swarm Optimization & Parallelism
**Target:** v1.1.0 | **Timeline:** Q2 2026

### Sprint Progress
| Sprint | Goal | Status |
|---|---|---|
| Sprint 1 — BaseScanner | Uniform scanner interface | ✅ Done — `packages/cherenkov/core/base_scanner.py` |
| Sprint 2 — Parallel Orchestration | asyncio + AIMD circuit breakers | ✅ Done — `circuit_breaker.py`, `ai_workflows_orchestrator.py` |
| Sprint 3 — TOKAMAK Sandbox | Docker isolation + PoC execution | 🔄 In Progress — `core/tokamak.py` exists, Docker wire-up pending |
| Sprint 4 — HITL Workflows | API pause gate + UI approval flow | ⏳ Not started |
| Sprint 5 — Compliance & Reporting | SAMA/EGY-FIN mapping + PDF/SARIF | ⏳ Not started |

## Active Work
- **Frontend dashboard** (`packages/cherenkov/web/`) — React 19 / Vite / Tailwind v4, live scan results, WebSocket events ✅
- **FastAPI backend** (`packages/cherenkov/api/main.py`) — `/api/v1/*` routes, `/ws/live` WebSocket, scan history ✅
- **Scanner graduation** — promoting `autonomous_generated/scanners/` into `packages/cherenkov/scanners/` under `BaseScanner` contract
- **TOKAMAK Docker** — `Dockerfile.tokamak` + `core/tokamak.py` need `Command` pattern + sandbox network isolation

## Agent Coordination
| Agent | Domain | Channel |
|---|---|---|
| Google Antigravity | Frontend React/Vite | localhost:3000 preview |
| Claude (GitHub Actions) | Code review, issue work | `@claude` in issues/PRs |
| Continue.dev (Qwen 3.5) | Local autonomous coding | `.continue/agents/` |
| Autonomous Pipeline | Scanner generation | `scripts/autonomous_roadmap_executor.py` daily |
| Claude Code (local) | Architecture, agentic coordination | This terminal |

## Module Ownership
See `.github/CODEOWNERS` for full ownership map.
