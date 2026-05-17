# CHERENKOV Project Status

## Build Health
| Check | Status |
|---|---|
| Tests | ✅ 146 passed, 36 skipped, 2 xfailed, 0 failures |
| Ruff lint | ✅ Passing |
| Ruff format | ✅ Passing |
| TypeScript (web) | ✅ Zero errors |
| Vite build | ✅ Clean (414 kB JS, 54 kB CSS) |

## Current Phase: Phase 2 — Swarm Optimization & Parallelism
**Target:** v1.1.0 | **Timeline:** Q2 2026

### Sprint Progress
| Sprint | Goal | Status |
|---|---|---|
| Sprint 1 — BaseScanner | Uniform scanner interface | ✅ Done |
| Sprint 2 — Parallel Orchestration | asyncio + AIMD circuit breakers | ✅ Done |
| Sprint 3 — TOKAMAK Sandbox | Docker isolation + PoC execution | ✅ Done — kali-rolling image, hardening flags, exec_run PoC |
| Sprint 4 — HITL Workflows | API pause gate + operator approval | ✅ Done — approve/reject/pending endpoints + SQLite WAL |
| Sprint 5 — Compliance & Reporting | SAMA/EGY-FIN mapping + PDF/SARIF | ✅ Done — 11 CWEs mapped, SARIF + PDF endpoints |
| Scanner Graduation | 6 production scanners under BaseScanner | ✅ Done — XXE, XSS, PathTraversal, FileUpload, SQLi, SSRF |

### Phase 2 Wiring (completed)
- **LATTICE vector store** — Qdrant + sentence-transformers; every finding indexed, FP auto-labelled, `/api/v1/lattice/similar` query endpoint
- **Rate limiting** — slowapi, 30 req/min on `/api/v1/scan`
- **Health endpoint** — live Ollama check, real Meissner state, TOKAMAK container count, LATTICE vector count
- **TOKAMAK hardening** — `--cap-drop=ALL --security-opt=no-new-privileges --read-only`, `exec_run` payload injection
- **Test ordering fix** — removed global `sys.modules["pydantic"] = MagicMock()` from `test_registry.py`
- **BackgroundTasks migration** — replaced `asyncio.create_task(to_thread(...))` with FastAPI `BackgroundTasks`

## Active Scanners (registered in ScannerRegistry)
| Scanner | CWE | Severity | SAMA CSF | EGY-FIN CSF |
|---|---|---|---|---|
| XXEScanner | CWE-611 | HIGH | 3.3.7 | PR.DS-2 |
| XSSScanner | CWE-79 | HIGH | 3.3.5 | PR.AC-4 |
| PathTraversalScanner | CWE-22 | HIGH | 3.2.1 | PR.AC-1 |
| FileUploadScanner | CWE-434 | HIGH | 3.3.10 | PR.DS-3 |
| SQLInjectionScanner | CWE-89 | CRITICAL | 3.3.6 | PR.DS-5 |
| SSRFScanner | CWE-918 | HIGH | 3.3.9 | PR.AC-5 |
| AndroidScanner | — | varies | — | — |
| IOSScanner | — | varies | — | — |

## Backlog (Phase 3 / v1.5.0)
- [ ] HITL UI — `PendingApprovalsPanel` badge count in `ForensicHeader` (Antigravity domain)
- [ ] Auth token fixture for `tests/packages/api/test_hitl_api.py` (2 xfail tests)
- [ ] Branch protection on `main` — require PR + CI pass
- [ ] `autonomous_generated/` cleanup — remove broken/duplicate files
- [ ] CSRF scanner (CWE-352) — next graduation candidate
- [ ] Open Redirect scanner (CWE-601) — next graduation candidate

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
