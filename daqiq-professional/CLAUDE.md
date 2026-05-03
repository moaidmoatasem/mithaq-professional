# DAQIQ — Claude Code Memory File
# Place this file at the ROOT of your daqiq-professional/ repo.
# Claude Code auto-loads it every session. This is how you carry
# the full context of your Claude.ai planning into Claude Code.

## Project identity

- Name: DAQIQ
- Repo: https://github.com/moaidmoatasem/daqiq-professional
- Type: Local-first AI-assisted security testing framework
- Language: Python 3.10+
- Current version: v0.1.1-security (Phase 0 complete)
- Development plan: docs/plan/development_plan.md

## Current phase

**Phase 1 — Repository & Foundation Cleanup (Weeks 1–2)**

## What works today (validated)

- 3 scanners: security headers, HTTP methods, HTTPS detection
- Basic CLI (daqiq_cli.py — argparse, to be replaced with Typer in Phase 2)
- Basic web dashboard (Flask — migrating to FastAPI in Phase 2)

## What does NOT work yet

- CrewAI orchestration (stub only, not integrated)
- PII redaction (not implemented)
- AI triage pipeline (scaffold only)
- 132 scanner candidates (unvalidated — live in candidates/)

## Critical security vulnerabilities (Phase 0 — fix first if not done)

1. Flask debug=True + host=0.0.0.0 in daqiq_web.py → CVSS 10.0 RCE
2. Stored XSS via innerHTML in web dashboard → CVSS 9.0
3. Bare except: handlers throughout scanner code → false negatives
4. No URL validation in SimpleScanner or /api/scan endpoint

## Architecture decisions (do not reverse these)

- FastAPI replaces Flask entirely (Phase 2)
- Scanner base class: src/daqiq/core/base_scanner.py
- Auto-discovery registry: src/daqiq/core/registry.py
- Async scan engine with rate limiting: src/daqiq/core/engine.py
- SQLite persistence at ~/.daqiq/results.db (no external deps)
- Typer + Rich CLI replacing argparse CLI
- Two Dockerfiles only: Dockerfile and Dockerfile.minimal
- Non-root user in all Docker containers (USER daqiq)

## Source of truth for code

src/daqiq/ is the ONLY canonical source directory.
daqiq/, daqiq-nexus-ai/ are dead and should be deleted.

## Scanner validation gate (required before any scanner merges to src/)

Every scanner in candidates/ must pass ALL of these before graduating:
1. Unit test: positive case (finds vuln with mocked HTTP)
2. Unit test: negative case (no false positive when vuln absent)
3. Integration test: fires on DVWA/bWAPP running in Docker
4. Does NOT fire on OWASP WebGoat safe pages
5. bandit: no new security issues
6. Docstring: CWE ID, description, technique, remediation

## Commands

- Run all tests:        pytest tests/
- Run unit tests only:  pytest tests/unit/
- Lint:                 ruff check .
- Security audit:       bandit -r src/ -ll
- Dep audit:            pip-audit
- Coverage report:      pytest --cov=daqiq --cov-report=html

## Dependency management

Single source: pyproject.toml
requirements.txt has been deleted.
aider-chat must NOT appear as a dependency.

## Git conventions

- Branch pattern: fix/<issue>, feat/<feature>, chore/<task>
- Commit prefix: fix:, feat:, chore:, docs:, test:
- Always run ruff + bandit before committing
- Tag security releases: vX.Y.Z-security

## What not to do

- Do not count candidates/ files as working scanners
- Do not update README before the code is working
- Do not use debug=True or host=0.0.0.0 anywhere
- Do not add features while open issues are unresolved
- Do not skip the validation gate for any scanner
- Do not race toward 132 scanners — 50 validated > 132 claimed

## Planning reference
Full planning conversation: https://claude.ai/chat/c86be7c3-891a-47f5-bcaf-bf759da12550
