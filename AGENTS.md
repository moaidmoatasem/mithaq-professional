# Agent Instructions: GitHub Workflows & Project Management

To ensure proper project management and adherence to standard GitHub workflows, all AI agents MUST strictly follow the guidelines below.

## 1. Branching Strategy
- **No Direct Commits**: NEVER commit directly to the `main` or `develop` branches.
- **Feature Branches**: Always create a separate branch for your work. Use the format `<type>/<issue-number>-<short-description>`.
  - Types: `feature`, `bugfix`, `hotfix`, `docs`, `refactor`.
  - Example: `git checkout -b feature/42-implement-new-scanner`

## 2. GitHub Project Management
You MUST use the tools and scripts below to manage the full project lifecycle.

### 2A. Label Taxonomy
Use these labels consistently. Every issue/PR must have at least one Type + Priority label.

| Category | Labels |
|---|---|
| **Type** | `epic`, `story`, `task`, `bug`, `feature`, `enhancement`, `chore`, `docs`, `refactor`, `test`, `security` |
| **Priority** | `priority:critical`, `priority:high`, `priority:medium`, `priority:low` |
| **Phase** | `phase-0` to `phase-5` |
| **Area** | `area:scanner`, `area:orchestrator`, `area:ui`, `area:api`, `area:docs`, `area:infra`, `area:agent`, `area:security` |
| **Status** | `status:blocked`, `status:in-progress`, `status:review-needed`, `status:done` |
| **AI** | `ai:generated`, `ai:reviewed`, `ai:autonomous` |
| **Sprint** | `sprint-1` through `sprint-5` |

### 2B. Milestones
All work must be linked to a milestone:
- `v1.0.0-rc1` — Sovereign Foundation (complete)
- `v1.1.0` — Swarm Concurrency
- `v1.5.0` — Enterprise Validation & HITL
- `v2.0.0` — Mobile Triad
- `v2.5.0` — Ecosystem Integration

### 2C. Agent PM Tool (`tools/gh_project_manager.py`)
```bash
# Create an issue with full metadata
python tools/gh_project_manager.py issue-create \
  --title "[TASK] Implement BaseScanner" \
  --body "Description" \
  --labels "task,phase-0,area:scanner,priority:high" \
  --milestone "v1.1.0" \
  --assignee "@me"

# Update issue labels/status/milestone
python tools/gh_project_manager.py issue-update \
  --issue 42 --add-labels "status:in-progress" --milestone "v1.1.0"

# List issues with filters
python tools/gh_project_manager.py issue-list --label "phase-0" --state open

# Create a release
python tools/gh_project_manager.py release-create \
  --tag "v1.1.0" --title "Swarm Concurrency" --notes "Release notes..." --discuss

# Generate status report
python tools/gh_project_manager.py status-report

# Generate changelog from merged PRs
python tools/gh_project_manager.py generate-changelog
```

### 2D. Issue Command Shortcuts
In any issue comment, use these commands:
- `/assign [@user]` — Assign the issue
- `/milestone <name>` — Set milestone
- `/label <label1, label2>` — Add labels
- `/phase <phase-n>` — Set phase
- `/priority <level>` — Set priority
- `/close` — Close the issue
- `/help` — Show available commands

### 2E. Weekly Agent PM Cadence
- **Monday**: Weekly sprint sync auto-creates issues from TODO.md
- **Daily**: Update status labels (`status:in-progress`, `status:review-needed`)
- **Friday**: Run status report, update TODO.md, close completed issues
- **Release Day**: Create release, milestone closes automatically, CHANGELOG.md updated

## 3. Commit Strategy
- **Atomic Commits**: Small, self-contained, single logical change.
- **Conventional Commits**: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`.
- **Issue Linking**: Reference issue number (e.g., `feat: add input validation (#42)`).

## 4. Merging Strategy
- **Pull Requests**: `gh pr create --title "..." --body "Closes #42" --base main`
- **No Self-Merging**: Wait for CI checks and HITL approval.

## 5. State Tracking
- `TODO.md`: Synced with GitHub Issues weekly
- `STATUS.md`: Current build/project status
- `CHANGELOG.md`: Updated automatically on release
- `AGENT_MEMORY.md`: Technical decisions and lessons learned

## 6. Pre-Commit Verification
- Format code (`black`, `ruff`) on modified files
- Run `pytest` for relevant tests
- Ensure pre-commit hooks pass
