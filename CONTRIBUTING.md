# Contributing to DAQIQ

Thank you for your interest in contributing to DAQIQ! 🚀

## Getting Started

1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/YOUR_USERNAME/daqiq-professional.git`
3. **Install** dependencies: `pip install -e ".[dev]"`
4. **Run tests**: `pytest --cov=daqiq`

## Development Workflow

### Creating a Feature

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and test
pytest --cov=daqiq --cov-report=term-missing

# Run linters
ruff check .
bandit -r daqiq/

# Commit with conventional commits
git commit -m "feat: Add your feature"
```

### Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Adding or updating tests
- `refactor:` Code refactoring
- `chore:` Maintenance tasks

## Code Quality Standards

### Test Coverage
- Maintain ≥80% coverage for new code
- Write unit tests for all new functions
- Add integration tests for new workflows

### Security
- All user inputs must pass through `Sanitizer`
- No hardcoded secrets or credentials
- Follow zero-trust principles

### Code Style
- Use Ruff for formatting: `ruff format .`
- Pass Bandit security checks: `bandit -r daqiq/`
- Type hints for all public functions (future requirement)

## Pull Request Process

1. **Update documentation** for any user-facing changes
2. **Add tests** with ≥80% coverage
3. **Run all checks**:
   ```bash
   pytest --cov=daqiq --cov-report=term-missing
   ruff check .
   bandit -r daqiq/
   ```
4. **Update CHANGELOG.md** with your changes
5. **Request review** from maintainers

## Areas for Contribution

### High Priority
- [ ] Phase 1: Daqiq Trace schema and recorder
- [ ] Phase 1: Local Executor integration
- [ ] Phase 1: Environment setup script (`setup_daqiq_env.sh`)

### Medium Priority
- [ ] Documentation improvements
- [ ] Additional scanner modules
- [ ] Test coverage improvements

### Low Priority (Future Phases)
- [ ] RAG knowledge base expansion
- [ ] PyQt Desktop UI
- [ ] Cloud provider integrations

## Questions?

- **Issues**: [GitHub Issues](https://github.com/moaidmoatasem/daqiq-professional/issues)
- **Discussions**: [GitHub Discussions](https://github.com/moaidmoatasem/daqiq-professional/discussions)

Thank you for contributing! 🙏
