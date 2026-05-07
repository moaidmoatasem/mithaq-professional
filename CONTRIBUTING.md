# Contributing to MITHAQ

Thank you for your interest in contributing to MITHAQ! We welcome contributions that align with our **Sovereign Security Standard**.

## 🛡️ Sovereign Contribution Guidelines

### 1. Zero-Egress Philosophy
All new features, agents, or scanners must operate under the "Zero-Egress" principle. If a feature requires internet access, it must be:
- Explicitly documented.
- Routed through the **SIYAADA** redaction layer.
- Controllable via the **DAREE3** network shield.

### 2. Forensic Proof (Al-Burhan)
Every security scanner must implement the `validate()` method to provide a non-destructive Proof of Concept (PoC). We do not accept scanners that only perform static analysis without a validation path.

### 3. Namespace Integrity
Always use the `mithaq` namespace. Legacy `daqiq` references are prohibited in new PRs.

## 🛠️ Development Workflow

### 1. Environment Setup
We recommend developing on a native Windows environment with WSL2 for containerized testing.

```powershell
# Initialize development environment
pip install -e .
pytest tests/
```

### 2. Atomic Design (UI)
If contributing to the web portal, follow the **Atomic Design** pattern in `src/mithaq/web/components/`. 
- **Atoms**: Pure UI elements.
- **Molecules**: Simple groups of atoms.
- **Organisms**: Functional business units.

### 3. Testing Requirements
- All new features must include `pytest` unit tests.
- High-impact logic must pass the `test_production_ready.py` quality gate.
- Ensure all CI/CD scans pass (CodeQL, Dependency Check).

## 📝 Pull Request Process

1. Fork the repository and create your branch from `main`.
2. Ensure your code follows the **MITHAQ Code of Conduct**.
3. Update the `CHANGELOG.md` with your changes.
4. Submit your PR with a detailed description of the security implications.

---
*MITHAQ: Accuracy is the root of sovereignty.*
