# CHERENKOV — Full Task Roadmap

**Stack:** Python 3.11 · FastAPI · React 19 / Vite / Tailwind v4 · SQLite WAL · Ollama  
**Target market:** EGY-FIN / SAMA sovereign security  
**Budget:** $0 (local inference only)

---

## Phase 1 — Foundation ✅ COMPLETE (v1.0.0-rc1)

| Task | File | Status |
|---|---|---|
| BaseScanner abstract class | `core/base_scanner.py` | ✅ |
| Severity / Finding / ScanResult schemas | `core/base_scanner.py` | ✅ |
| MEISSNER circuit breaker (AIMD) | `core/circuit_breaker.py` | ✅ |
| ABLATION redactor / sanitizer | `core/ablation/` | ✅ |
| TOKAMAK execution sandbox stub | `core/tokamak.py` | ✅ stub |
| SQLite WAL storage helpers | `core/storage/database.py` | ✅ |
| FastAPI server skeleton | `api/main.py` | ✅ |
| `/api/v1/*` REST routes | `api/main.py` | ✅ |
| `/ws/live` WebSocket hub | `api/main.py` | ✅ |
| React dashboard (HUD) | `web/src/` | ✅ |
| Vite proxy + api.ts client | `web/src/lib/api.ts` | ✅ |
| ForensicHeader + NodeStatusRow | `web/src/components/organisms/` | ✅ |
| TacticalOperationsPanel + ThreatIntelPanel | `web/src/components/organisms/` | ✅ |
| CI pipeline (ruff, pytest, bandit, CodeQL) | `.github/workflows/` | ✅ |
| Agent coordination files | `AGENTS.md`, `GEMINI.md`, `.agents/` | ✅ |

---

## Phase 2 — Swarm Optimization (v1.1.0) 🔄 IN PROGRESS — Q2 2026

### 2A · TOKAMAK Docker Sandbox [Issue #174]

| # | Task | File |
|---|---|---|
| 2A-1 | `Command` + `TokamakResult` dataclasses | `core/tokamak.py` |
| 2A-2 | `Tokamak.execute()` — docker run `--network none`, capture stdout/stderr | `core/tokamak.py` |
| 2A-3 | SHA-256 trace signing: `sha256(stdout+stderr+timestamp).hexdigest()` | `core/tokamak.py` |
| 2A-4 | Cryptographic shred receipt on teardown (overwrite + truncate + JSON receipt) | `core/tokamak.py` |
| 2A-5 | `POST /api/v1/sandbox/execute` + `GET /api/v1/sandbox/status` | `api/main.py` |
| 2A-6 | Unit tests (mock subprocess, assert 64-char trace_hash, receipt schema) | `tests/unit/test_tokamak.py` |

### 2B · Backend Hardening [Issue #177]

| # | Task | File |
|---|---|---|
| 2B-1 | `list_scans(limit)` — query SQLite instead of `_scan_history` list | `core/storage/database.py` |
| 2B-2 | `/api/v1/scans/history` reads from DB (survives restart) | `api/main.py` |
| 2B-3 | `/api/v1/health` nodes — ping `localhost:11434/api/tags` (timeout 1s) | `api/main.py` |
| 2B-4 | `/api/v1/health` meissner.state from `meissner_hub.state.value` | `api/main.py` |
| 2B-5 | Register WS callback in `Meissner._transition_to_open()` → broadcast `circuit_breaker` event | `core/circuit_breaker.py` + `api/main.py` |
| 2B-6 | Unit tests for DB persistence and health endpoint | `tests/unit/test_api_health.py` |

### 2C · Scanner Graduation [Issue #178]

| # | Task | File |
|---|---|---|
| 2C-1 | Graduate `xxe_scanner.py` → `scanners/xxe_scanner.py` + unit test | `scanners/xxe_scanner.py` |
| 2C-2 | Graduate `pathtraversalscanner.py` + unit test | `scanners/path_traversal_scanner.py` |
| 2C-3 | Graduate `fileuploadscanner.py` + unit test | `scanners/file_upload_scanner.py` |
| 2C-4 | Graduate `networkvulnerabilityscanner.py` + unit test | `scanners/network_scanner.py` |
| 2C-5 | Graduate `cicdintegrationscanner.py` + unit test | `scanners/cicd_scanner.py` |
| 2C-6 | Register all 5 in `ScannerRegistry` | `core/registry.py` |
| 2C-7 | `GET /api/v1/scanners` — list registered scanners + metadata | `api/main.py` |

### 2D · Parallel Orchestration Hardening

| # | Task | File |
|---|---|---|
| 2D-1 | `ScanEngine.scan_all()` — true asyncio gather across all registered scanners | `core/engine.py` |
| 2D-2 | Per-scanner timeout isolation (one scanner failure doesn't kill others) | `core/engine.py` |
| 2D-3 | Broadcast `scan_progress` WS events per scanner completion | `core/engine.py` + `api/main.py` |
| 2D-4 | Integration test: parallel scan finishes faster than sequential | `tests/integration/test_parallel_scan.py` |

---

## Phase 3 — Production Hardening & HITL (v1.5.0) ⏳ NEXT — Q3 2026

### 3A · HITL Approval Gate

| # | Task | File |
|---|---|---|
| 3A-1 | `findings_pending` SQLite table (WAL) | `core/storage/database.py` |
| 3A-2 | `FindingApproval` Pydantic model | `api/main.py` |
| 3A-3 | Hook `_run_scan()`: insert CRITICAL/HIGH findings → `findings_pending` + broadcast | `api/main.py` |
| 3A-4 | `POST /api/v1/findings/{id}/approve` | `api/main.py` |
| 3A-5 | `POST /api/v1/findings/{id}/reject` | `api/main.py` |
| 3A-6 | `GET /api/v1/findings/pending` | `api/main.py` |
| 3A-7 | `PendingApprovalsPanel` organism (Approve/Reject buttons, severity badge) | `web/src/components/organisms/` |
| 3A-8 | `ForensicHeader` badge — red pulse when pending count > 0 | `web/src/components/organisms/ForensicHeader.tsx` |
| 3A-9 | `usePendingApprovals(intervalMs)` hook | `web/src/hooks/useMetrics.ts` |
| 3A-10 | Unit tests for all three endpoints | `tests/unit/test_hitl_api.py` |

### 3B · Compliance Mapper

| # | Task | File |
|---|---|---|
| 3B-1 | `packages/cherenkov/compliance/__init__.py` | `compliance/` |
| 3B-2 | `ComplianceMapper` — static dict: CWE → OWASP / SAMA_CSF / EGY_FIN_CSF / DORA | `compliance/mapper.py` |
| 3B-3 | Cover 20+ CWEs: 79, 89, 22, 352, 611, 287, 798, 502, 200, 918, 77, 78, 94, 306, 312, 319, 434, 601, 732, 918 | `compliance/mapper.py` |
| 3B-4 | `GET /api/v1/reports/{scan_id}/sarif` — SARIF 2.1.0 export | `api/main.py` |
| 3B-5 | `GET /api/v1/reports/{scan_id}/pdf` — local PDF (reportlab, zero cloud) | `api/main.py` |
| 3B-6 | Unit tests: CWE mapping coverage + SARIF schema validation | `tests/unit/test_compliance_mapper.py` |

### 3C · WORM Audit Vault

| # | Task | File |
|---|---|---|
| 3C-1 | Enforce WAL mode + `PRAGMA journal_mode=WAL` on all DB connections | `core/storage/database.py` |
| 3C-2 | `AuditEntry` table: immutable rows (no UPDATE/DELETE permitted) | `core/storage/database.py` |
| 3C-3 | Auto-append every scan, finding, approval, rejection as audit entry | `api/main.py` |
| 3C-4 | `GET /api/v1/audit` — chronological audit log endpoint | `api/main.py` |
| 3C-5 | Unit test: verify no row can be mutated after insert | `tests/unit/test_audit_vault.py` |

### 3D · SSO / RBAC Portal

| # | Task | File |
|---|---|---|
| 3D-1 | JWT middleware for `/api/v1/*` — Bearer token validation | `api/middleware/auth.py` |
| 3D-2 | Role enum: `OPERATOR`, `ANALYST`, `ADMIN` | `api/middleware/auth.py` |
| 3D-3 | `POST /api/v1/auth/token` — local credential store (bcrypt, no cloud IdP) | `api/main.py` |
| 3D-4 | Role-gate: only `OPERATOR`+ can approve/reject findings | `api/main.py` |
| 3D-5 | Frontend: login page, token storage in `sessionStorage` (not localStorage) | `web/src/` |

---

## Phase 4 — Mobile Triage (v2.0.0) ⏳ Q4 2026 – Q1 2027

### 4A · Android Scanner

| # | Task | File |
|---|---|---|
| 4A-1 | `MobileScanner` abstract class extending `BaseScanner` | `core/mobile_scanner.py` |
| 4A-2 | APKTool wrapper — decompile APK, extract manifest + smali | `scanners/mobile/apktool_scanner.py` |
| 4A-3 | Androguard wrapper — static analysis, permission audit | `scanners/mobile/androguard_scanner.py` |
| 4A-4 | Hardcoded secrets detector (API keys, tokens in smali/java) | `scanners/mobile/secrets_scanner.py` |
| 4A-5 | TOKAMAK integration — run mobile payloads in `--network none` container | `core/tokamak.py` |

### 4B · iOS Scanner

| # | Task | File |
|---|---|---|
| 4B-1 | IPA unpacker + plist parser | `scanners/mobile/ipa_scanner.py` |
| 4B-2 | Binary analysis — detect insecure flags (PIE, ARC, stack canary) | `scanners/mobile/binary_scanner.py` |
| 4B-3 | Transport Security checker (NSAllowsArbitraryLoads audit) | `scanners/mobile/ats_scanner.py` |

### 4C · Frida / Runtime

| # | Task | File |
|---|---|---|
| 4C-1 | Frida hook generator — produce JS hook from CWE/finding | `core/frida_generator.py` |
| 4C-2 | Drozer PoC executor under TOKAMAK sandbox | `core/tokamak.py` |
| 4C-3 | Hook output → Finding with `trace_hash` signature | `core/tokamak.py` |

### 4D · Mobile Dashboard

| # | Task | File |
|---|---|---|
| 4D-1 | `MobileTargetForm` organism — APK/IPA upload + package name | `web/src/components/organisms/` |
| 4D-2 | `MobileResultsPanel` — permission tree, binary flags, findings | `web/src/components/organisms/` |
| 4D-3 | `POST /api/v1/mobile/scan` — accepts file upload | `api/main.py` |

---

## Phase 5 — Ecosystem Integration (v2.5.0) ⏳ 2027

### 5A · CI/CD Integration

| # | Task | File |
|---|---|---|
| 5A-1 | `cherenkov-action` GitHub Action — run scan on PR, post findings as review | `.github/actions/cherenkov-scan/` |
| 5A-2 | SARIF upload to GitHub Security tab from CI scan | `.github/actions/cherenkov-scan/action.yml` |
| 5A-3 | CLI: `cherenkov scan <url> --format sarif` | `cli/main.py` |
| 5A-4 | CLI: `cherenkov report <scan_id> --format pdf` | `cli/main.py` |

### 5B · Local SIEM Integration

| # | Task | File |
|---|---|---|
| 5B-1 | Syslog forwarder (RFC 5424, local network only, zero egress) | `core/siem/syslog_forwarder.py` |
| 5B-2 | CEF (Common Event Format) serializer for findings | `core/siem/cef_serializer.py` |
| 5B-3 | Splunk HEC connector (local Splunk instance) | `core/siem/splunk_connector.py` |

### 5C · Multi-Node Mesh

| # | Task | File |
|---|---|---|
| 5C-1 | Node discovery — mDNS broadcast on local subnet | `core/mesh/discovery.py` |
| 5C-2 | Scan job distribution — partition target list across nodes | `core/mesh/distributor.py` |
| 5C-3 | Result aggregation — merge findings from all nodes, dedup | `core/mesh/aggregator.py` |
| 5C-4 | Mesh dashboard panel — node map, job distribution | `web/src/components/organisms/MeshPanel.tsx` |

---

## Milestone Summary

| Milestone | Phases | Key deliverable | Target |
|---|---|---|---|
| v1.0.0-rc1 | 1 | Trident architecture + HUD | ✅ Done |
| v1.1.0 | 2 | Parallel swarm + TOKAMAK + 5 scanners | Q2 2026 |
| v1.5.0 | 3 | HITL + compliance + WORM vault + RBAC | Q3 2026 |
| v2.0.0 | 4 | Mobile Android/iOS + Frida | Q4 2026 |
| v2.5.0 | 5 | CI/CD action + SIEM + mesh | Q1 2027 |

## Issue Tracking Convention

Every task row → one GitHub issue.  
Title: `[Ph<N>] <task description>`  
Labels: `phase-<N>`, `area:<domain>`, `priority:<level>`  
Branch: `feat/<issue>-<slug>`  
All task files: `.agents/tasks/issue-<N>.md`
