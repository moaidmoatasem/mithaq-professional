# Contributing

We welcome contributions from the community. CHERENKOV follows a strict development workflow with mandatory TDD and human review for security-critical changes.

## Getting Started

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes following [code standards](../standards/CODE_STANDARDS.md)
4. Run tests: `pytest`
5. Submit a pull request

## Commit Convention

Use [conventional commits](https://www.conventionalcommits.org/):

```
feat(scanner): Add API security scanner
fix(auth): Resolve token expiration bug
docs(readme): Update installation instructions
test(xss): Add tests for reflected XSS detection
```

## Review & Approval

All changes follow the [Development Workflow](../processes/DEVELOPMENT_WORKFLOW.md):

1. PM defines user story
2. Architect designs solution
3. Developer implements (TDD)
4. QA validates
5. Code review completed

Changes to MEISSNER, ABLATION, TOKAMAK, or authentication require **mandatory human review**.

## Development Setup

```bash
pip install -e ".[dev]"
pre-commit install
```

See the [Development Workflow](../processes/DEVELOPMENT_WORKFLOW.md) for the complete process, and [Code Standards](../standards/CODE_STANDARDS.md) for style and testing requirements.
