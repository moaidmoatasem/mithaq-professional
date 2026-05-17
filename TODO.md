# CHERENKOV TODO — Phase 2 Active Sprint

## Sprint 2: Orchestration Hardening [DONE ✅]
- [x] `ScanEngine.scan_all()` — true asyncio gather across all registered scanners (#182)
- [x] Per-scanner timeout isolation (one scanner failure doesn't kill others) (#182)
- [x] Broadcast `scan_progress` WS events per scanner completion (#182)
- [x] Integration test: parallel scan finishes faster than sequential (#182)
- [x] Target-level circuit breaker (Meissner) integration (#182)

## Sprint 3: TOKAMAK Execution Sandbox [DONE ✅]
- [x] Wire `core/tokamak.py` to `Dockerfile.tokamak` — pass sandbox a `Command` payload, return signed JSON receipt
- [x] Implement cryptographic erasure ("shred receipt") after sandbox teardown per CLAUDE.md invariant
- [x] Write `tests/unit/test_tokamak.py` — verify: payload reaches sandbox, output is SHA-256 signed, receipt is valid JSON
- [x] Add `GET /api/v1/sandbox/status` FastAPI endpoint so dashboard can poll TOKAMAK state

## Sprint 4: HITL Workflows [DONE ✅]
- [x] `POST /api/v1/findings/{id}/approve` — pause workflow, require operator signature before HIGH/CRITICAL PoC execution
- [x] `GET /api/v1/findings/pending` — list findings awaiting approval
- [x] `POST /api/v1/findings/{id}/reject` — reject finding with operator audit
- [x] Store pending state in SQLite (WAL mode) so restarts don't lose pending approvals
- [x] Frontend: `PendingApprovalsPanel` organism — badge count in `ForensicHeader`, full list in sidebar

## Sprint 5: Compliance & Reporting [DONE ✅]
- [x] Build `packages/cherenkov/compliance/` mapper: CWE/CVE → SAMA CSF / EGY-FIN CSF / DORA / OWASP Top 10 (19 CWEs)
- [x] `GET /api/v1/reports/{scan_id}/sarif` — export scan as SARIF 2.1 JSON
- [x] `GET /api/v1/reports/{scan_id}/pdf` — generate local PDF audit report (reportlab, zero cloud)
- [x] Map compliance framework to `NewScanForm.tsx` `compliance` dropdown options
- [x] Unit tests — 14 tests covering all 4 frameworks, map_all(), coverage()
- [x] Business Process Mapping — `ProcessMapper`: 7 business processes → process flows → CWEs → compliance frameworks
- [x] `GET /api/v1/processes` — list available business processes by category
- [x] `GET /api/v1/processes/{id}/controls` — get security controls per process step
- [x] `GET /api/v1/processes/{id}/report` — generate process-specific risk & compliance report

## Backend Hardening [DONE ✅]
- [x] Move `_scan_history` from in-memory list to SQLite WAL vault (survives restart)
- [x] `GET /api/v1/health` — wire `meissner.state` from real `CircuitBreakerRegistry` instead of hardcoded `"CLOSED"`
- [x] `GET /api/v1/health` — wire `nodes` to actual Ollama process check (ping localhost:11434)
- [x] Broadcast `circuit_breaker` WebSocket events from `Meissner._transition_to_open()`

## Phase 4: Mobile Triage [DONE ✅]
- [x] Implement IPA/ATS/Binary scanners for iOS/Android forensic auditing
- [x] Create `MobileDashboard` with specialized binary ingestion port
- [x] Implement Frida/Drozer hooks for dynamic analysis in TOKAMAK

## Phase 5: Enterprise Orchestration [DONE ✅]
- [x] `SIEMForwarder` — Syslog (CEF) and Splunk HEC event streaming
- [x] `MeshManager` — Multi-node discovery and distributed scan coordination
- [x] `LatticeBridge` — Semantic Vector Intelligence via Qdrant and local embeddings

## Scanner Graduation [ONGOING]
- [ ] Audit `autonomous_generated/scanners/` — identify the 5-10 best implementations
- [ ] Refactor them to inherit `BaseScanner`, add proper `scan()` async method
- [ ] Move graduated scanners to `packages/cherenkov/scanners/` with unit tests
- [ ] Register them in `ScannerRegistry` so they run on every `/api/v1/scan`

## Agentic Infrastructure [DONE ✅]
- [x] `AGENTS.md` — agent roles, branching roles, label taxonomy
- [x] `CODEOWNERS` — updated to `packages/cherenkov/*` layout
- [x] `claude.yml` — @claude GitHub Actions integration
- [x] `autonomous-dev.yml` — daily scanner generation pipeline
- [x] `.continue/agents/new-config.yaml` — Continue.dev Qwen 3.5 local agent

## Backlog
- [ ] Branch protection on `main` — require PR + CI pass (currently pushing direct to main)
- [ ] `agent_state/` cleanup — archive stale checkpoint files
- [ ] `autonomous_generated/` — remove broken/duplicate files (many are non-functional)
