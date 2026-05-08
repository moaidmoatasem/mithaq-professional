# Agent Instructions: GitHub Workflows & Project Management

To ensure proper project management and adherence to standard GitHub workflows, all AI agents MUST strictly follow the guidelines below.

## 1. Branching Strategy
- **No Direct Commits**: NEVER commit directly to the `main` or `develop` branches.
- **Feature Branches**: Always create a separate branch for your work. Use the format `<type>/<issue-number>-<short-description>`.
  - Types: `feature`, `bugfix`, `hotfix`, `docs`, `refactor`.
  - Example: `git checkout -b feature/42-implement-new-scanner`

## 2. GitHub Project Management (via `gh` CLI)
You are required to use the GitHub CLI (`gh`) to manage the project state.
- **Issues**: Ensure an issue exists for your task. If not, create one: `gh issue create --title "..." --body "..."`
- **Assignments**: Assign the issue to yourself or the relevant user: `gh issue edit <issue> --add-assignee "@me"`
- **Labels**: Apply semantic labels to issues and PRs (e.g., `bug`, `enhancement`, `security`, `documentation`): `gh issue edit <issue> --add-label "enhancement"`
- **Milestones & Projects**: Link issues and PRs to active milestones and GitHub Projects to maintain a clear roadmap.
- **Wikis**: For architectural decisions, major guides, or extensive documentation, update the repository Wiki.

## 3. Commit Strategy
- **Atomic Commits**: Commits should be small, self-contained, and represent a single logical change.
- **Conventional Commits**: Follow the conventional format (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`).
- **Issue Linking**: Reference the corresponding issue number in the commit message (e.g., `feat: add input validation (#42)`).

## 4. Merging Strategy
- **Pull Requests (PRs)**: Always create a Pull Request to merge your feature branch.
  - Create the PR via CLI: `gh pr create --title "..." --body "Closes #42" --base main`
- **Metadata**: Add reviewers, assignees, labels, and milestones to the PR.
- **No Self-Merging**: Do not merge your own PRs. Wait for CI checks (tests, linters, security scans) to pass and for Human-in-the-Loop (HITL) approval.

## 5. State Tracking & Documentation
You must keep the project tracking files up to date at all times to maintain a clear source of truth:
- `TODO.md`: Check off completed tasks and add newly discovered ones.
- `STATUS.md`: Update with current build/project status.
- `PROJECT_SUMMARY.md`: Update if major features or architectural shifts occur.
- `CHANGELOG.md`: Document user-facing changes, features, and fixes.
- `AGENT_MEMORY.md`: Record context, technical decisions, and lessons learned for future sessions.
- `SESSION_ACHIEVEMENTS.md` / `TONIGHT_ACHIEVEMENTS.md`: Log the specific tasks completed during your session.

## 6. Pre-Commit Verification
Always run verification checks before committing:
- Format code (e.g., `black`, `ruff`) only on the specific files modified to avoid massive diffs.
- Run tests (`pytest`) related to your changes.
- Ensure all required pre-commit instructions are followed.
