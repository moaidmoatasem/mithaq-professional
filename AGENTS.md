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
| **Kilo** | VS Code Kilo sessions | Backend / multi-file refactors in its own worktrees under `.kilo/worktrees/` | `vast-liquid`, `gratis-cheque`, etc. (Kilo-generated) |

---

## 1. Branching Rules (NON-NEGOTIABLE)

- **NEVER commit directly to `main`.** All changes go through a branch + PR.
- **Exception**: Agentic state files (`STATUS.md`, `TODO.md`, `AGENT_MEMORY.md`) may be committed to main by the coordinating Claude Code session only when no feature work is included.
- Branch naming: `<type>/<issue-number>-<short-description>`
  - Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`
  - Example: `feat/42-tokamak-docker-sandbox`
- Create PR with `gh pr create`, reference the issue: `Closes #<N>`
- **Do not spawn a parallel branch for an active task.** Before creating a
  branch, run `git branch -a` and `gh pr list` for the same scope. Continue
  the existing branch instead of creating `feat/foo-<timestamp>` duplicates.
- Delete your branch (local + remote) after the PR merges.

---

## 1b. Working Trees

- Need an isolated checkout? Use `git worktree add`, never a parallel clone.
- Worktrees live under `.worktrees/<agent>-<slug>/`. One branch ↔ one worktree.
  If `git worktree list` already shows the branch, reuse it.
- When done: `git worktree remove <path> && git worktree prune`.
- **Never operate on the repo via a `\\wsl.localhost\...` UNC path from
  Windows.** Pack/repack will fail with permission errors. Always run git
  inside WSL on native ext4.

---

## 1c. Rebase Discipline & Branch Alignment

- Keep topic branches rebased onto `origin/main`. Do **not** merge `main`
  back into a topic branch.
- After rebasing a pushed branch: `git push --force-with-lease` (never plain
  `--force`, never on `main`).
- Never amend/rewrite commits that already exist on `origin/main`.
- Squash fixup/wip commits before opening or merging a PR.
- **To realign every local branch onto `main`** (after long-running multi-agent
  divergence), run `scripts/align-branches.sh` from inside WSL. It rebases each
  branch, aborts on conflict, logs results to `.git/align-log/`, and pushes
  nothing. Review the conflict list and resolve those branches manually.

---

## 1d. Untracked Artifacts

- `data/`, `models/`, `cherno-docs/`, and any generated runtime output are
  **never committed**. Add to `.gitignore` if missing.
- If an agent needs to share generated data, document the producer in `docs/`
  rather than checking the artifact in.
- Secrets, `.env`, credentials, key material: never committed, never logged,
  never sent to an external model (see CHERENKOV ABLATION in `CLAUDE.md`).

---

## 1e. Claim Tickets (conflict prevention)

Before editing any file, every agent MUST:

1. **Check for an existing claim** on the files it intends to touch:
   ```bash
   gh issue list -l claim/active --search "<path-or-keyword>"
   ```
2. **If a claim exists** that overlaps your files, do not edit. Either:
   - Comment on the existing claim offering to take it over (if the prior
     agent's token expired or the work is stalled), then update the issue
     body to reflect the new owner; or
   - Pick a different task.
3. **If no claim exists**, open one before editing:
   ```bash
   gh issue create -l claim/active -t "[claim] <task-slug>" -b "
   Branch: ai/<task-slug>
   Files:
     - packages/cherenkov/api/main.py
     - packages/cherenkov/api/middleware/auth.py
   Agent: <identity>
   Started: <UTC timestamp>
   "
   ```
4. **Close the claim** when the PR merges or you abandon the task.

**Why this works across token rotation:** claims are GitHub issues, not
agent identities. If Claude's token expires mid-task, Jules can take over
the same claim and the same branch — no ownership change, no conflict.

---

## 1f. Domain Hints (advisory, not enforced)

Routing preference when multiple agents are available. Any agent may
fulfill any role; this just suggests the first-choice match.

| Domain | Paths | First-choice agent |
|---|---|---|
| frontend | `packages/cherenkov/web/`, `cherno-docs/` | Antigravity |
| backend | `packages/cherenkov/api/`, `packages/cherenkov/core/` | Claude Code |
| scanners | `packages/cherenkov/scanners/` | Autonomous Pipeline |
| infra | `deploy/`, `.github/`, `Dockerfile*`, `docker-compose*.yml` | Claude Code |
| docs | `cherno-docs/`, `*.md` at repo root | Jules / Claude Code |

These are hints, not hard locks. Token expired? Any agent can step in —
just update the claim ticket.

---

## 1g. Touch Budget (per PR)

To keep PRs reviewable and merge-fast (small PRs merge faster → less
parallel drift → fewer conflicts):

- **≤8 files** changed per PR (excluding lockfiles).
- **≤400 lines** added+deleted per PR (excluding lockfiles).
- Enforced by `.github/workflows/pr-budget.yml`.
- To exceed: maintainer (Moaid) adds the `large-pr-approved` label and
  the PR description must justify why splitting is not feasible.

If your task is larger than the budget, **split into stacked PRs**:
land each piece independently, rebase the next on the previous.

---

## 1h. Worktree Spawning

Use `scripts/spawn_agent_worktree.sh <task-slug>` to create an isolated
worktree. Worktrees are named by **task slug**, not agent identity:

```
../cherenkov-worktrees/auth-refactor/        ← any agent
../cherenkov-worktrees/scanner-cve-2024-X/   ← any agent
```

When one agent's token expires, the next agent `cd`s into the same
worktree and continues. No file ownership change, no merge.

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

## 4b. Kilo — Worktree-Based Agent

**Trigger**: Kilo sessions inside VS Code (`.kilo/agent-manager.json`)

**Your domain**: Backend Python and multi-file refactors inside your own
worktree under `.kilo/worktrees/<branch>/`. You do NOT modify the primary
checkout.

**Task list discipline (MOST IMPORTANT)**:
- The authoritative task list is **`TODO.md`** at the repo root, with
  supporting state in `STATUS.md` and `AGENT_MEMORY.md`.
- Before starting any work: `git fetch origin && git rebase origin/main`
  inside your worktree, then re-read `TODO.md`. Pick the next unchecked
  item in dependency order (see the "Dependency Order" block in `TODO.md`).
- Do not start a task marked `BLOCKED` or whose listed dependencies are
  still unchecked.
- When you finish an item: tick the checkbox in `TODO.md`, update
  `STATUS.md` if it changes phase/build state, and include the `TODO.md`
  diff in the same commit as the feature work — never in a separate
  "update todo" commit.
- If `TODO.md` is missing in your worktree, copy it from the primary
  checkout (`~/cherenkov-professional/TODO.md`) before doing anything else.
  Do not invent a separate task list.

**Workflow rules**:
- One Kilo session ↔ one worktree ↔ one branch. Do not switch the worktree
  to a different branch mid-session.
- Use `scripts/align-branches.sh` (run from the primary checkout, inside
  WSL) to keep your worktree's branch rebased onto `main`. The script
  rebases pinned branches inside their own worktrees.
- Push with `git push --force-with-lease` after rebase. Never `--force`.
- Stay out of `.kilo/worktrees/<other-branch>/` — that belongs to another
  Kilo session.

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

**Documentation changes**:
```bash
markdownlint docs/ --ignore docs/assets/
python dev_crew/doc_gate.py validate --manifest docs/manifest.json
mkdocs build --strict
python scripts/sync_docs.py validate
```

## 8. Documentation Compliance (All Agents)

When generating or modifying documentation, every agent MUST:

1. **Structure** — Follow the Writing Style Guide at `docs/development/writing-style.md`
2. **Cross-References** — All `[text](path)` links must resolve. Run `doc_gate.py validate` before committing.
3. **Diagrams** — Every architecture doc MUST include at least one Mermaid diagram.
4. **Manifest** — Every new doc MUST be registered in `docs/manifest.json`.
5. **Naming** — File names must be `kebab-case.md`. Titles must match H1.
6. **Signature** — Each AI-generated doc MUST declare `Agent: <name>` in a frontmatter comment.
7. **Sync** — Root governance files (`CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md`) are the SSOT. Edits to `docs/governance/` copies will be overwritten by `scripts/sync_docs.py`.

Violations of these rules are **Sovereign Breaches** and will block PRs via the doc gate CI check.

---

## 8. State Files (keep current)

| File | Owner | Update cadence |
|---|---|---|
| `STATUS.md` | Claude Code (coordinating) | After each sprint milestone |
| `TODO.md` | Claude Code (coordinating) | Weekly or when sprint changes |
| `AGENT_MEMORY.md` | Claude Code (coordinating) | After architectural decisions |
| `AGENTS.md` | Claude Code (coordinating) | When agent roster changes |
| `CHANGELOG.md` | Automated (release-drafter) | On release |

---

## 9. In-Product AI Agents (Phase 3 — under construction)

These are **runtime** agents that the CHERENKOV platform itself invokes during
a scan. They are distinct from the **developer** agents above (Jules, Claude
Code, Antigravity), which only write code. Runtime agents live under
`packages/cherenkov/agents/` and are routed via the LiteLLM proxy at
`http://localhost:4000`.

| Agent | Role | Model (alias → backing) | File |
|---|---|---|---|
| **Security Architect** | Engagement planning, reasoning over findings | `architect` → `foundation-sec-8b-reasoning` | `agents/architect.py` |
| **Red Team** | Offensive task generation, exploit PoC drafting | `red-team` → `redsage-dpo` / WhiteRabbitNeo | `agents/red_team.py` |
| **SecOps** | Compliance mapping (EGY-FIN CSF, OWASP), defensive recs | `secops` → Trendyol-Cybersecurity | `agents/secops.py` |
| **KINETIC executor** | Local code generation for scanner automation | `code-smart` → `qwen2.5-coder:7b` | inline |
| **LATTICE embedder** | Vectorize scan traces into Qdrant | `embed` → `nomic-embed-text` | `ai/lattice_bridge.py` |

### Runtime agent rules

1. **All model calls route through LiteLLM** (`http://localhost:4000`). Never
   call Ollama directly from product code — model swaps must be config-only.
2. **External LLMs (TENSOR tier) require ABLATION first.** No raw payload
   leaves the perimeter. Cloud fallback (`cloud-fallback` alias) is gated.
3. **Red Team output is untrusted** until TOKAMAK executes the proposed PoC
   in an isolated container and produces a SHA-256 proof hash.
4. **SecOps output is advisory** until a human compliance officer signs off
   (HITL approval, surfaced via `PendingApprovalsPanel`).
5. **Engagement plans from the Architect** are persisted to the
   `cherenkov_traces` table alongside their resulting scan.

### Authoritative prompt library

The full, copy-paste session prompts (context block, per-section briefs,
GitHub issue scripts, Open WebUI preset) live in
[`docs/AGENT_PROMPTS.md`](./docs/AGENT_PROMPTS.md). Treat it as the SSOT for
agent task wording. Update it when prompts change — do not maintain
per-agent prompt copies.
