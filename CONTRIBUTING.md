# Contributing to CHERENKOV / MITHAQ

Thank you for your interest in contributing! We welcome contributions that align with our **Sovereign Security Standard** and strictly follow our designated flows, roles, rules, and best practices.

## 🛡️ Sovereign Contribution Guidelines

### 1. Zero-Egress Philosophy
All new features, agents, or scanners must operate under the "Zero-Egress" principle. If a feature requires internet access, it must be:
- Explicitly documented.
- Routed through the **ABLATION** redaction layer.
- Controllable via the **MEISSNER** network shield.

### 2. Clean Architecture
Strictly separate concerns:
- **CLI/Web:** Should only interact with `orchestration_api.py`.
- **API:** Handles business logic and agent routing.
- **Persistence (`ResultStore`):** Only accessed by the API layer.
- **Scanners:** Must inherit from `BaseScanner` to ensure auto-discovery via `ScannerRegistry`.

### 3. Namespace Integrity
Always use the correct `cherenkov` namespace.

## 🛠️ Development Workflow & Branching Strategy

### 1. Environment Setup
```bash
# Initialize development environment
pip install -e ".[dev]"
pytest tests/unit/
```

### 2. GitHub Project Management & Branching Process
All contributors must follow our strict GitHub Flow:
- **Issues & Milestones:** Ensure your work is tracked by an active GitHub Issue and linked to a project board.
- **Branching Strategy:**
  - NEVER commit directly to `main` or `develop`.
  - Create feature branches following the format: `feature/<issue-number>-<description>`, `bugfix/<issue-number>-<description>`, or `docs/<issue-number>-<description>`.
- **Commits:** Use Conventional Commits (e.g., `feat:`, `fix:`, `docs:`).

### 3. Pull Request & Review Process
- **Create PR:** Open a Pull Request against `develop` (or `main` if hotfix). Use the provided PR Template.
- **Documentation:** Provide clear documentation for the done work within the PR description.
- **CI/CD Checks:** All automated checks must pass before a review is requested. This includes:
  - Unit Tests (`pytest`)
  - Code Formatting (`black`, `flake8`)
  - Security Scans (`bandit`, `CodeQL`, `Trivy`)
- **Review:** Wait for Human-in-the-Loop (HITL) PR reviewer approval before merging.
- **Do Not Merge Your Own PRs.**

### 4. Code Quality & Best Practices
- **Test-Driven Development (TDD):** New features must have corresponding tests.
- **Documentation:** All functions and classes must have clear docstrings (Google Style).
