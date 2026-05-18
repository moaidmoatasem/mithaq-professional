# CHERENKOV Agent Coordination Guide

This file is read by every AI agent working on this repo. Follow it precisely.

---

## Agent Roster & Domain Ownership

| Agent | Trigger | Primary Domain | Branch Prefix |
|---|---|---|---|
| **Antigravity (Google IDE)** | Gravity preview, local dev | `packages/cherenkov/web/` frontend | `feat/web-*` |
| **Claude (GitHub Actions)** | `@claude` in issues/PRs | Code review, targeted fixes, issue work | `claude/*` |
| **Claude Code (local)** | Terminal sessions | Architecture, agentic coordination, multi-file refactors | `claude/*` |
| **Autonomous Pipeline** | Daily cron 2AM UTC | Scanner generation (`autonomous_roadmap_executor.py`) | `auto-dev/<run>` |

---

## 1. Branching Rules (NON-NEGOTIABLE)

- **NEVER commit directly to `main`.** All changes go through a branch + PR.
- **Exception**: Agentic state files (`STATUS.md`, `TODO.md`, `AGENT_MEMORY.md`) may be committed to main by the coordinating Claude Code session only when no feature work is included.
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

## 4. Autonomous Pipeline — Scanner Factory

**Trigger**: `scripts/autonomous_roadmap_executor.py --batch-size 3` (daily cron)

**Output**: New scanner files in `packages/cherenkov/autonomous_generated/scanners/`

**Rules**:
- Output must pass `ruff format`
- File names must be `snake_case.py`
- Each file must contain exactly one class inheriting `BaseScanner`
- PR title: `feat: AI-generated scanner — <scanner_name>`
- Label: `ai:generated`, `area:scanner`, `priority:medium`

---

## 5. GitHub Project Management

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
- `v1.1.0` — Swarm Concurrency (current — Phase 2)
- `v1.5.0` — Enterprise Validation & HITL (Phase 3)
- `v2.0.0` — Mobile Triage (Phase 4)
- `v2.5.0` — Ecosystem Integration (Phase 5)

### Issue Commands (in comments)
```
/assign @me
/label area:scanner, priority:high
/milestone v1.1.0
/close
```

---

## 6. Commit Standards

- Format: `<type>(<scope>): <description> (#<issue>)`
- Example: `feat(scanners): graduate XSS scanner to BaseScanner contract (#47)`
- Co-author line: `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>`
- Python: run `ruff format` before every commit
- TypeScript: run `tsc --noEmit` before every commit

---

## 7. Pre-Commit Checklist

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

## 8. State Files (keep current)

| File | Owner | Update cadence |
|---|---|---|
| `STATUS.md` | Claude Code (coordinating) | After each sprint milestone |
| `TODO.md` | Claude Code (coordinating) | Weekly or when sprint changes |
| `AGENT_MEMORY.md` | Claude Code (coordinating) | After architectural decisions |
| `AGENTS.md` | Claude Code (coordinating) | When agent roster changes |
| `CHANGELOG.md` | Automated (release-drafter) | On release |
