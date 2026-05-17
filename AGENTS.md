# CHERENKOV Agent Coordination Guide

This file is read by every AI agent working on this repo. Follow it precisely.

---

## Agent Roster & Domain Ownership

| Agent | Trigger | Primary Domain | Branch Prefix |
|---|---|---|---|
| **Antigravity (Google IDE)** | Gravity preview, local dev | `packages/cherenkov/web/` frontend | `feat/web-*` |
| **Claude (GitHub Actions)** | `@claude` in issues/PRs | Code review, targeted fixes, issue work | `claude/*` |
| **Claude Code (local)** | Terminal sessions | Architecture, agentic coordination, multi-file refactors | `claude/*` |
| **Continue.dev (Qwen 3.5)** | VS Code / IDE | Autonomous coding, scanner graduation | `auto-dev/*` |
| **Jules (Google)** | `@jules` in issues | Autonomous issue implementation, branch + PR | `jules/*` |
| **Autonomous Pipeline** | Daily cron 2AM UTC | Scanner generation (`autonomous_roadmap_executor.py`) | `auto-dev/<run>` |

---

## 1. Branching Rules (NON-NEGOTIABLE)

- **NEVER commit directly to `main`.** All changes go through a branch + PR. No exceptions.
- Branch naming: `<type>/<issue-number>-<short-description>`
  - Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`
  - Example: `feat/42-tokamak-docker-sandbox`
- Create PR with `gh pr create`, reference the issue: `Closes #<N>`

---

## 2. Antigravity (Google IDE) — Frontend Agent

**Your domain**: `packages/cherenkov/web/src/`

**How you work**:
- Vite dev server runs on port `3000`
- Preview connects to FastAPI backend on port `8000` via Vite proxy (configured in `vite.config.ts`)
- Never hard-code `localhost:8000` — use `API_BASE` and `getWsUrl()` from `@/src/lib/api.ts`
- Import pattern: `@/src/lib/X`, `@/src/hooks/X`, `@/src/components/X`
- HMR: respect `DISABLE_HMR` env var (already wired in vite.config)

**Current priority tasks** (pick from TODO.md Sprint 4):
- `PendingApprovalsPanel` organism — show findings awaiting HITL approval
- Badge count in `ForensicHeader` for pending approvals

**Do NOT touch**:
- `packages/cherenkov/api/` (backend Python) — that's a different domain
- `packages/cherenkov/core/` or `packages/cherenkov/scanners/`

---

## 3. Claude (GitHub Actions) — Issue & PR Agent

**Trigger**: Any comment containing `@claude` in issues or PRs.

**Your scope**:
- Answer questions about architecture referencing `CLAUDE.md`, `AGENT_MEMORY.md`
- Write or fix code when asked in an issue
- Create a branch, commit, open a PR — never merge your own PR
- Always run ruff format before committing Python: `ruff format packages/`
- Always check TS: `cd packages/cherenkov/web && npm run lint`

**Label every PR you open with**: `ai:generated`, `ai:autonomous`, and the appropriate `area:*` label.

---

## 4. Continue.dev / Local Autonomous Agent — Scanner Graduation

**Your domain**: `packages/cherenkov/scanners/` and `packages/cherenkov/core/`

**Current priority** (Sprint 3 backlog):
1. Pick one scanner from `packages/cherenkov/autonomous_generated/scanners/` that has a real scan implementation
2. Refactor it to inherit `BaseScanner` (from `packages/cherenkov/core/base_scanner.py`)
3. Add `async def scan(self, target: str, timeout: float = 10.0) -> ScanResult`
4. Write a unit test in `tests/unit/test_<scanner_name>.py`
5. Register it in `packages/cherenkov/core/registry.py`
6. Open a PR: branch `feat/<N>-graduate-<scanner_name>`

**Code standards**:
- Strong typing (PEP 484). Use `from __future__ import annotations` where needed.
- Run `ruff format` + `ruff check` before committing.
- NEVER import from `src.cherenkov.*` — use `cherenkov.*`

---

## 5. Autonomous Pipeline — Scanner Factory

**Trigger**: `scripts/autonomous_roadmap_executor.py --batch-size 3` (daily cron)

**Output**: New scanner files in `packages/cherenkov/autonomous_generated/scanners/`

**Rules**:
- Output must pass `ruff format`
- File names must be `snake_case.py`
- Each file must contain exactly one class inheriting `BaseScanner`
- PR title: `feat: AI-generated scanner — <scanner_name>`
- Label: `ai:generated`, `area:scanner`, `priority:medium`

---

## 6. GitHub Project Management

### Label Taxonomy
Every issue and PR MUST have at least one of each:

| Category | Labels |
|---|---|
| **Type** | `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `security` |
| **Priority** | `priority:critical`, `priority:high`, `priority:medium`, `priority:low` |
| **Phase** | `phase-2`, `phase-3`, `phase-4`, `phase-5` |
| **Area** | `area:scanner`, `area:api`, `area:ui`, `area:infra`, `area:agent`, `area:security`, `area:compliance` |
| **Status** | `status:in-progress`, `status:review-needed`, `status:blocked` |
| **AI** | `ai:generated`, `ai:autonomous` (if AI-authored) |

### Milestones
- `v0.1.1-cherenkov` — Phase 1/2: Core scaffolding + 6 graduated scanners (current, 146 tests passing)
- `v1.0.0` — Phase 3: TOKAMAK forensics + HITL workflow
- `v1.5.0` — Phase 4: Enterprise Validation
- `v2.0.0` — Phase 5: Mobile Triage / Ecosystem Integration

### Issue Commands (in comments)
```
/assign @me
/label area:scanner, priority:high
/milestone v1.1.0
/close
```

---

## 7. Commit Standards

- Format: `<type>(<scope>): <description> (#<issue>)`
- Example: `feat(scanners): graduate XSS scanner to BaseScanner contract (#47)`
- Co-author line: `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>`
- Python: run `ruff format` before every commit
- TypeScript: run `tsc --noEmit` before every commit

---

## 8. Pre-Commit Checklist

**Python changes**:
```bash
ruff format packages/
ruff check packages/ --ignore W,S,B
pytest -m "not (integration or ai_generated)" --tb=short
```

**TypeScript/React changes**:
```bash
cd packages/cherenkov/web
npm run lint        # tsc --noEmit
npx vite build      # production build must pass
```

---

## 9. State Files (keep current)

| File | Owner | Update cadence |
|---|---|---|
| `STATUS.md` | Claude Code (coordinating) | After each sprint milestone |
| `TODO.md` | Claude Code (coordinating) | Weekly or when sprint changes |
| `AGENT_MEMORY.md` | Claude Code (coordinating) | After architectural decisions |
| `AGENTS.md` | Claude Code (coordinating) | When agent roster changes |
| `CHANGELOG.md` | Automated (release-drafter) | On release |
