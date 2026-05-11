# cherenkov Development TODO

## Phase 0: Foundation — COMPLETE
- [x] Repository setup
- [x] Agent rules configuration
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
- [x] Stale src/cherenkov/ removed

## v1.0.0-rc1 — Sovereign Foundation (Milestone 4)
Issues: #16, #17, #18, #19, #20
- [x] #16 Hardware-Agnostic Environment Setup Script
- [x] #17 Dynamic Model Quantization & Benchmarking
- [ ] #18 Context-Preserving Sanitization Bridge
- [x] #19 Define Cherenkov Trace Schema
- [x] #20 Trace Recorder & State Engine

## v1.1.0 — Swarm Concurrency (Milestone 5)
Issues: #21, #22, #23, #24, #25, #88, #89, #90, #91, #102
- [ ] #21 Expose Professional Scanners as Local Tools
- [ ] #22 Stateless Local Executor
- [ ] #23 Burhan Validator (Stateless MiniGPT)
- [ ] #24 First End-to-End "Hello Cherenkov" Scenario
- [ ] #25 Agentic Dev Orchestrator (PM-Agent)
- [ ] #88 HTTP Client for Groq/Gemini
- [ ] #89 APKTool Wrapper for Mobile Scanning
- [ ] #90 Androguard Integration
- [ ] #91 Replace print() with logging in scanners
- [ ] #102 Wire CI Pipeline (lint, typecheck, test)

## v1.5.0 — Enterprise Validation & HITL (Milestone 6)
Issues: #93, #94, #95, #96
- [ ] #93 Compliance-as-Code Engine
- [ ] #94 WORM SQLite Audit Vault
- [ ] #95 Human-in-the-Loop Workflows for Critical Vulns
- [ ] #96 Enterprise SSO/RBAC for Local Portal

## v2.0.0 — Mobile Triad (Milestone 7)
Issues: #97, #98, #99
- [ ] #97 Mobile Scanner: APKTool + Androguard Integration
- [ ] #98 Frida Hook Generator
- [ ] #99 Drozer PoC Executor under Tokamak Sandbox

## v2.5.0 — Ecosystem Integration (Milestone 8)
Issues: #100, #101
- [ ] #100 Local PDF Report Generator
- [ ] #101 SARIF Exporter for CI/CD Integration

## GitHub PM Infrastructure — SETUP COMPLETE
- [x] Label taxonomy (41 labels, 7 categories)
- [x] 5 version milestones (v1.0.0-rc1 → v2.5.0)
- [x] 6 YAML issue forms + CODEOWNERS
- [x] Agent PM Python CLI (tools/gh_project_manager.py)
- [x] 6 PM automation workflows
- [x] Project board "CHERENKOV Sovereign Roadmap" linked
- [x] Wiki pushed (10 pages)
- [x] Discussions enabled
- [x] AGENTS.md updated with PM lifecycle

## Technical Debt / Quick Wins
- [ ] #91 Replace `print()` calls in scanners with logging
- [ ] #102 Wire CI pipeline (GitHub Actions: lint, typecheck, test)
