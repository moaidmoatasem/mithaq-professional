# cherenkov Development TODO

## Phase 0: Foundation (Week 1) - IN PROGRESS
- [x] Repository setup
- [x] Agent rules configuration
- [x] CloudInstruction Pydantic schema
- [x] AblationSanitizer with HMAC
- [ ] Test suite (6/6 tests passing)

## GitHub PM Infrastructure (Completed)
- [x] Comprehensive label taxonomy (40+ labels, 7 categories)
- [x] 5 milestones mapped to release strategy
- [x] 6 YAML issue forms (bug_report, feature_request, task, epic, security_advisory, user_story)
- [x] CODEOWNERS file
- [x] Agent PM Python CLI (tools/gh_project_manager.py)
- [x] 6 PM automation workflows:
  - Project Board Automation
  - Weekly Sprint Sync
  - Roadmap Sync
  - Release Automation
  - Issue Command Automation (/assign, /milestone, etc.)
  - Stale Issue Management
- [x] Wiki/discussions setup scripts
- [x] Updated AGENTS.md with PM lifecycle instructions

## Pending Setup (Requires gh auth)
- [ ] Run scripts/setup_github_pm.ps1 to create labels, milestones, project, wiki
- [ ] Enable Discussions in repo settings

## Phase 1: Multi-Provider Orchestration (Week 2-8)
- [ ] HTTP client for Groq/Gemini
- [ ] Fallback logic
- [ ] Circuit breaker
- [ ] Rate limit enforcer
- [ ] Integration tests

## Phase 2: Tool Integration (Week 9-20)
- [ ] APKTool wrapper
- [x] Fix eval() injection vulnerability
- [x] Merge Cloudflare configuration (PR #66)
- [ ] Androguard integration
- [ ] Frida hook generator
- [ ] Drozer PoC executor

## Phase 3: Tokamak Validation (Week 21-28)
- [ ] PoC runner | Evidence verification | False positive elimination

## Phase 4: Security Hardening (Week 29-35)
- [ ] Supply chain audit | SBOM generation | Penetration testing

## Phase 5: Enterprise Readiness (Week 36-41)
- [ ] PyQt6 UI | PDF reporter | SARIF exporter | DIVA benchmark

## Current Sprint
**Focus:** GitHub PM infrastructure — COMPLETE
**Next task:** Authenticate gh CLI and apply remote setup
