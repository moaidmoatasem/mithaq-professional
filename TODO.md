# CHERENKOV Development TODO

> Last updated: 2026-05-24 by Antigravity (C2 Hub handover)
> Source of truth for issues: `.agents/context.md` + GitHub Issues

---

## Phase 0: Foundation — ✅ COMPLETE

- [x] Repository setup + agent rules
- [x] CloudInstruction Pydantic schema
- [x] AblationSanitizer with HMAC
- [x] Package restructure (`packages/cherenkov/`)
- [x] Test restructure (`tests/packages/`)
- [x] Design System (tokens + Atomic Design)
- [x] Error hierarchy (15 exception types)
- [x] Logging (print→logging in all hand-written code)
- [x] God-class splitting (AgentRegistry, WorkflowScheduler, WorkflowExecutor)
- [x] Type annotations (all hand-written modules)
- [x] Event bus constructor injection
- [x] Stale `src/cherenkov/` removed

## v1.0.0-rc1 — Sovereign Foundation — ✅ COMPLETE

- [x] #16 Hardware-Agnostic Environment Setup Script
- [x] #17 Dynamic Model Quantization & Benchmarking
- [x] #18 Context-Preserving Sanitization Bridge
- [x] #19 Define Cherenkov Trace Schema
- [x] #20 Trace Recorder & State Engine

## v1.0.0-rc2 — Documentation Finalization — ✅ COMPLETE

- [x] Full mkdocs alignment
- [x] Architecture docs, Design System docs, Technical Spec, Premortem
- [x] SSOT, Sovereign Blueprint, Master Plan
- [x] `site/` build artifacts untracked

---

## v1.1.0 — Swarm Optimization (Phase 2) — 🔄 IN PROGRESS

### P0 — Critical (do first, Phase 2 is blocked until done)

- [x] #230 Remove cloud configs — MEISSNER enforcement (MERGED)
- [x] #232 Root cleanup — remove stale root artifacts (MERGED)
- [x] #234 Harden .gitignore
- [/] #236 Scanner registry auto-discovery (PR in progress)
- [/] #237 Scan result aggregation pipeline (PR in progress)
- [ ] #238 Wire POST /api/v1/scan (BLOCKED — depends on #236 + #237)
- [ ] #239 CI matrix 146+ tests pass (do LAST in Phase 2)

### P1 — Remaining Phase 2

- [ ] #231 GitHub repo metadata
- [ ] #233 Align GEMINI.md with AGENTS.md roster
- [ ] #235 Canonicalize CHANGELOG

### Dependency Order

```
#230 ✅ → #234 ✅ → #236 → ┐
                         ├→ #238 → #239
                  #237 → ┘
#232 ✅ (independent)
#231, #233, #235 (independent, low priority)
```

---

## v1.5.0 — Enterprise Validation & HITL (Phase 3)

> ⛔ Do NOT start Phase 3 until all Phase 2 P0 items are closed.

### P0 — Critical infrastructure

- [ ] #246 TOKAMAK SQLite WAL logger
- [ ] #247 Wire Cherenkov Trace signing (depends #237 + #246)

### P1 — Scanner graduation (high)

- [ ] #240 Graduate NetworkVulnerabilityScanner
- [ ] #241 Verify XXE scanner contract
- [ ] #245 Verify SSRF scanner contract

### P2 — Scanner graduation (medium)

- [ ] #242 Graduate CVE Database Scanner
- [ ] #243 Graduate CI/CD Integration Scanner
- [ ] #244 Graduate AttackChainDetector

---

## v2.0.0 — Mobile Triage (Phase 4) — ⏳ Q4 2026

- [ ] #97 Mobile Scanner: APKTool + Androguard Integration
- [ ] #98 Frida Hook Generator
- [ ] #99 Drozer PoC Executor under Tokamak Sandbox

## v2.5.0 — Ecosystem Integration (Phase 5) — ⏳ 2027

- [ ] #100 Local PDF Report Generator
- [ ] #101 SARIF Exporter for CI/CD Integration

---

## Infrastructure & Agentic Coordination

- [x] Label taxonomy (41 labels, 7 categories)
- [x] 5 version milestones (v1.0.0-rc1 → v2.5.0)
- [x] 6 YAML issue forms + CODEOWNERS
- [x] Agent PM Python CLI
- [x] 6 PM automation workflows
- [x] Agentic Handover Protocol (`docs/development/agentic-handover-protocol.md`)
- [x] AgentStateStore (`agent_state/*.json`)
- [ ] C2 Hub (Control Tower) — agent-agnostic coordination layer (this handover)

## Technical Debt / Quick Wins

- [x] #91 Replace `print()` calls in scanners with logging
- [x] #102 Wire CI pipeline (GitHub Actions: lint, typecheck, test)
- [ ] Resolve PR #351 merge conflict in `database.py`
- [ ] Move state files from `archive/sessions/` to repo root (this PR)
