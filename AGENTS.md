# CHERENKOV Agent Coordination Guide
Version: 2.0 | Updated: May 2026

This file is read by every AI agent. Follow it precisely.

---

## Current Project State (May 2026)

- **Phase:** 1 (Hygiene) + Phase 2 (Core Wiring) — IN PROGRESS
- **Version:** v0.1.1-cherenkov
- **Validated scanners:** 5 (`header_scanner`, `security_headers`, `http_methods`, `tls_detection`, `unified_scanner`)
- **Broken:** `/health` hardcoded, `/ws/live` missing, TOKAMAK never runs, LATTICE empty

---

## Agent Roster & Domain Ownership

| Agent | Trigger | Domain | Branch Prefix |
|---|---|---|---|
| **Jules (Google)** | Manual task assignment | Scanner validation, DVWA gate, LATTICE wiring | `feat/jules-*` |
| **Claude Code (local)** | Terminal sessions | Architecture, multi-file refactors, API wiring | `claude/*` |
| **Antigravity (IDE)** | Local dev | `packages/cherenkov/web/` only | `feat/web-*` |
| **Gemini (AI Studio)** | Manual | React FE components | `feat/web-*` |
| **OpenCode** | VS Code | Scanner graduation from `candidates/` | `auto-dev/*` |
| **Autonomous Pipeline** | Daily cron 2AM UTC | Scanner generation to `autonomous_generated/` | `auto-dev/*` |

---

## 1. Branching Rules (NON-NEGOTIABLE)

- NEVER commit directly to `main`. All changes: branch → PR → Moaid merges.
- Branch format: `<type>/<N>-<description>`
- Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `security`
- Example: `feat/A1-live-health-endpoint`
- Create PR: `gh pr create --title "..." --body "Closes #N"`
- **Moaid is the ONLY person who merges PRs.**

> **Exception removed:** State files (`STATUS.md`, `TODO.md`, `AGENT_MEMORY.md`) must also go through PRs. No more direct-to-main exceptions.

---

## 2. Jules — Scanner Validation Factory

**Domain:** scanner candidates, LATTICE bridge, DVWA validation

**Environment available in Jules VM:**
- DVWA: `http://localhost:80` (admin/password)
- WebGoat: `http://localhost:8090`
- Qdrant: `http://localhost:6333`
- Ollama: `http://localhost:11434` (llama3.2:3b)

**Task format:**
```
Single task only: [specific task].
export PYTHONPATH=$PYTHONPATH:$(pwd)/packages
Use docker exec -i (NOT -it) for container commands.
Imports: from cherenkov.* (not src.cherenkov.*)
Run ruff format + bandit before committing.
Branch: feat/[issue-N]-[description]
Report: files changed, tests passed, blockers.
```

**Do NOT touch:** `packages/cherenkov/web/` (Antigravity domain)

---

## 3. Claude Code (local) — Architecture & Wiring

**Domain:** API endpoints, core wiring, multi-file changes

**Session start:** `python scripts/sync_context.py && cat .cherenkov_context`

**Task format:**
```
Read CLAUDE.md only. Single task: [X].
export PYTHONPATH=$PYTHONPATH:$(pwd)/packages
Canonical path: packages/cherenkov/ (NOT src/)
After: ruff format, pytest, git push, report.
```

**Do NOT touch:** `packages/cherenkov/web/` unless explicitly asked

---

## 4. Antigravity — Frontend Only

**Domain:** `packages/cherenkov/web/src/`

- Vite dev on port 3000, proxies to FastAPI on port 8000
- Never hardcode `localhost:8000` — use `API_BASE` from `@/src/lib/api.ts`
- Import pattern: `@/src/lib/X`, `@/src/hooks/X`, `@/src/components/X`
- Run: `tsc --noEmit && npx vite build` before every commit
- **Do NOT touch:** `packages/cherenkov/api/` or any Python files

---

## 5. OpenCode — Scanner Graduation

**Domain:** `packages/cherenkov/scanners/` and `packages/cherenkov/core/`

**Process per scanner:**
1. Pick from `packages/cherenkov/autonomous_generated/scanners/`
2. Refactor to inherit `BaseScanner`
3. Implement `async scan(target: str, timeout: float = 10.0) -> ScanResult`
4. Write unit test in `tests/unit/test_<scanner_name>.py`
5. Register in `packages/cherenkov/core/registry.py`
6. PR: `feat/<N>-graduate-<scanner_name>`

---

## 6. Autonomous Pipeline — Scanner Factory

**Trigger:** daily cron 2AM UTC
**Output:** `packages/cherenkov/autonomous_generated/scanners/`

**Rules:**
- Must pass `ruff format`
- `snake_case.py` filenames
- Exactly one class inheriting `BaseScanner` per file
- PR label: `ai:generated`, `area:scanner`, `priority:medium`

---

## 7. GitHub Issue Labels

Every issue/PR needs at least one from each category:

| Category | Options |
|---|---|
| Type | `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `security` |
| Priority | `priority:critical`, `priority:high`, `priority:medium`, `priority:low` |
| Phase | `phase-1`, `phase-2`, `phase-3`, `phase-4`, `phase-5`, `phase-6` |
| Area | `area:scanner`, `area:api`, `area:ui`, `area:infra`, `area:agent`, `area:security`, `area:compliance` |
| Status | `status:in-progress`, `status:review-needed`, `status:blocked` |
| AI | `ai:generated`, `ai:autonomous` (if AI-authored) |

---

## 8. Milestones (Updated)

| Milestone | Target | Focus |
|---|---|---|
| `v0.1.1-cherenkov` | NOW | Phase 1 hygiene + Phase 2 wiring |
| `v0.2.0` | +8 weeks | 20 validated scanners + demo works |
| `v0.3.0` | +16 weeks | TOKAMAK executes real PoCs |
| `v1.0.0` | +32 weeks | Cairo pilot + EGY-FIN CSF |
| `v2.0.0` | +52 weeks | Mobile + OWASP LLM |

---

## 9. Commit Standards

Format: `<type>(<scope>): <description> (#<N>)`
Example: `feat(api): wire /health with live Ollama data (#A1)`
Co-author: `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>`

**Python pre-commit:**
```bash
ruff format packages/
ruff check packages/ --ignore W,S,B
pytest -m "not (integration or ai_generated)" --tb=short
```

**TypeScript pre-commit:**
```bash
cd packages/cherenkov/web
tsc --noEmit
npx vite build
```

---

## 10. Files Agents Must NOT Delete

**KEEP at root:** `README.md`, `AGENTS.md`, `ARCHITECTURE.md`, `CHERENKOV_SSOT.md`, `CLAUDE.md`, `CHANGELOG.md`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md`, `DESIGN_SYSTEM.md`, `LICENSE`, `Dockerfile`, `Dockerfile.tokamak`, `pyproject.toml`, `mkdocs.yml`, `setup.sh`, `.env.example`, `.gitignore`, `.pre-commit-config.yaml`, `.gitattributes`, `CHERENKOV_*.md`

**DELETED (do not recreate):** `fly.toml`, `railway.json`, `render.yaml`, `mcp_config.json`, `launch_perfection.sh`, `celebration_scan.sh`, `CLAUDE_COMPRESSED.md`, `CLAUDE_V4.1.md`, `docker-compose.agents.yml`, `docker-compose.optimized.yml`, `Dockerfile.agent`, `Dockerfile.optimized`, `Dockerfile.simple`

---

## 11. State Files

| File | Owner | When to update |
|---|---|---|
| `CLAUDE.md` | Claude Code | On phase change or architectural decision |
| `AGENTS.md` | Moaid + Claude Code | When agent roster or process changes |
| `CHANGELOG.md` | Release Drafter (automated) | On every release |
| `docs/development/roadmap.md` | Claude Code | On phase status change |

> `STATUS.md`, `TODO.md`, `AGENT_MEMORY.md`: archived to `archive/sessions/` — no longer maintained at root.
