# CHERENKOV Project Status
**Last updated:** 2026-05-17

---

## P0 Blockers — Must fix before any demo

| Issue | Item | Impact |
|---|---|---|
| [#222](https://github.com/moaidmoatasem/cherenkov-professional/issues/222) | TOKAMAK never executes a real PoC | Core value prop broken |
| [#221](https://github.com/moaidmoatasem/cherenkov-professional/issues/221) | `/api/v1/health` returns hardcoded data | HUD shows fake data |
| [#224](https://github.com/moaidmoatasem/cherenkov-professional/issues/224) | LATTICE not wired — Qdrant zero vectors | Adaptive learning inactive |
| [#223](https://github.com/moaidmoatasem/cherenkov-professional/issues/223) | Root directory — 50+ dev artifacts | First impression is chaos |

---

## Build Health

| Check | Status |
|---|---|
| Tests | ✅ 68 passed, 7 skipped |
| Ruff lint | ✅ Passing |
| Ruff format | ✅ Passing |
| TypeScript | ✅ Zero errors |
| Vite build | ✅ 414 kB JS, 54 kB CSS |

---

## Phase Progress

### Phase 1 — Foundation ✅ Complete
BaseScanner, MEISSNER, ABLATION, SQLite WAL, FastAPI, React HUD, CI.

### Phase 2 — Swarm Optimization 🔴 P0 Blocked (v1.1.0, Q2 2026)

| Sprint | Goal | Status |
|---|---|---|
| 2A — TOKAMAK Docker | Docker isolation + PoC execution + shred receipt | 🔴 Stub only — issue #222 |
| 2B — Backend Hardening | Real health metrics, SQLite persistence, WS circuit breaker | 🔴 Health hardcoded — issue #221 |
| 2C — Scanner Graduation | 5 scanners → BaseScanner contract, ScannerRegistry | 🟡 Partial |
| 2D — Parallel Orchestration | asyncio gather, timeout isolation, WS progress events | ✅ Done (PR #208) |

### Phase 3 — Production Hardening ⏳ Q3 2026
HITL approval gate, EGY-FIN compliance mapper, WORM audit vault, RBAC.
**Blocked by Phase 2 completion.**

### Phase 4+ — Mobile, CI/CD, Mesh ⏳ Q4 2026+
Not started. No open issues. Phase 2 must be complete first.

---

## Open Issues

| # | Priority | Title |
|---|---|---|
| [#221](https://github.com/moaidmoatasem/cherenkov-professional/issues/221) | P0 🔴 | `/api/v1/health` — wire real metrics |
| [#222](https://github.com/moaidmoatasem/cherenkov-professional/issues/222) | P0 🔴 | TOKAMAK — Docker sandbox not wired |
| [#223](https://github.com/moaidmoatasem/cherenkov-professional/issues/223) | P0 🔴 | Root directory cleanup |
| [#224](https://github.com/moaidmoatasem/cherenkov-professional/issues/224) | P0 🔴 | LATTICE — Qdrant not wired |
| [#186](https://github.com/moaidmoatasem/cherenkov-professional/issues/186) | P1 | SSO / RBAC Portal (Phase 3) |

---

## Agent Coordination

| Agent | Domain | Status |
|---|---|---|
| Claude Code (local) | Architecture, P0 fixes, issue creation | Active |
| Jules (Google) | Backend Python — TOKAMAK, LATTICE | Configured via `GEMINI.md` |
| Continue.dev | Local scanner graduation | Configured via `.continue/config.yaml` |
| OpenCode | General backend tasks | Configured via `opencode.jsonc` |
| Claude GitHub | Code review on PRs | `@claude` in issues/PRs |
| Autonomous Pipeline | Scanner generation | `scripts/autonomous_roadmap_executor.py` |

Agent tasks: `.agents/tasks/issue-N.md` — read `.agents/context.md` first.

---

## Module Ownership

See `.github/CODEOWNERS` and `AGENTS.md` for full domain ownership map.
