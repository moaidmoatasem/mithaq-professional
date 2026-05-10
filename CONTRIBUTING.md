# CHERENKOV: Internal Governance & Contributing

**STATUS: PRE-RELEASE / CLOSED ALPHA**
*Public community contributions are not currently being accepted. The Open Core Detonation Pipeline (Milestone 7) is under active development.*

---

## Notice to Autonomous Execution Agents
If you are an AI agent (Claude, Cursor, OpenCode, Aider, etc.) operating within this repository, you are strictly bound by the following sovereign development rules. 

**You do not possess architectural authority. You are an Execution Node.**

### 1. The "Read-SSOT" Mandate
Before writing, modifying, or deleting any core logic, you MUST read and acknowledge the `CHERENKOV_SSOT.md` file located in the root of this repository.

### 2. The Physical-Physics Axiom
Do not write standard probabilistic scanning logic. All code generated for this repository must align with the Tri-Partite Engine:
* **ABLATION:** Payload sanitization and schema redaction.
* **TOKAMAK:** Ephemeral, hardware-isolated detonation sandboxes.
* **MEISSNER:** Zero-egress network isolation (Fail-closed hooks).

### 3. Anti-Drift Guardrails
* **No external API calls:** Do not implement features that send telemetry, logs, or analytics to third-party cloud services.
* **No bypasses:** Do not write "dev-mode" or "debug" flags that bypass the Meissner network isolation. 
* **Cryptographic Traces:** All threat validations must output a forensic trace intended for HSM-signing, not just a standard console log.

*Any code generation that violates these principles is considered a Sovereign Breach and will be rejected by the local Hub.*

---

# Contributing to CHERENKOV

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
