# Daqiq Security Framework

📚 [View Complete Documentation](./daqiq-professional/MASTER_DOCUMENTATION.md) 

[![Tests](https://github.com/moaidmoatasem/daqiq-professional/actions/workflows/test.yml/badge.svg)](https://github.com/moaidmoatasem/daqiq-professional/actions/workflows/test.yml)
[![Docker Build](https://github.com/moaidmoatasem/daqiq-professional/actions/workflows/docker.yml/badge.svg)](https://github.com/moaidmoatasem/daqiq-professional/actions/workflows/docker.yml)


**AI-powered security testing framework with multi-agent orchestration**

[![Tests](https://img.shields.io/badge/tests-passing-success)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-91.78%25-brightgreen)](htmlcov/)
[![Python](https://img.shields.io/badge/python-3.12-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

---

## 🎯 Project Vision

Daqiq is a comprehensive security testing framework that combines:
- **AI-powered analysis** using local LLMs (Ollama/DeepSeek)
- **Multi-agent orchestration** with specialized security roles
- **Zero-trust sanitization** preventing secrets leakage
- **Cloud-native execution** across AWS, Azure, GCP

---

## ✅ Phase 0: Foundation (COMPLETE)

### Implemented Components

#### 1. **CloudInstruction Schema** ✅
Pydantic v2 schema for secure agent instructions with built-in validators.

```python
from daqiq.schemas.cloud_instruction import CloudInstruction

instruction = CloudInstruction(
    task_id="task-123",
    action="analyze_smali",
    target="app.apk",
    confidence=0.95,
    reasoning="Decompiled APK for security analysis"
)
```

**Security Features:**
- AWS key detection and rejection
- JWT token validation
- Prompt injection prevention
- Confidence score validation (0.0-1.0)

#### 2. **SanitizedOutput Schema** ✅
Structured output for sanitization results.

```python
from daqiq.schemas.sanitized_output import SanitizedOutput

output = SanitizedOutput(
    original_text="Key: AKIAIOSFODNN7EXAMPLE",
    sanitized_text="Key: [REDACTED]",
    secrets_found=["AWS_KEY:AKIAIOSFODNN7EXAMPLE"],
    sanitization_applied=True
)
```

#### 3. **Sanitizer Component** ✅
Real-time secret detection and redaction.

```python
from daqiq.core.sanitizer import Sanitizer

sanitizer = Sanitizer()
result = sanitizer.sanitize("My key is AKIAIOSFODNN7EXAMPLE")

print(result.sanitized_text)  # "My key is [REDACTED]"
print(result.secrets_found)   # ["AWS_KEY:AKIAIOSFODNN7EXAMPLE"]
```

**Detects:**
- AWS access keys (AKIA pattern)
- JWT tokens (eyJ pattern)
- Prompt injection attempts

---

## 📊 Test Coverage

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=daqiq --cov-report=html

# Integration tests only
pytest tests/integration/ -v
```

**Current Status:**
- **Unit Tests:** 13/13 passing
- **Integration Tests:** 6/6 passing  
- **Total Coverage:** 91.78%

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone <repository-url>
cd daqiq-security-framework

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate    # Windows

# Install in development mode
pip install -e ".[dev]"
```

### Basic Usage

```python
from daqiq.core.sanitizer import Sanitizer
from daqiq.schemas.cloud_instruction import CloudInstruction

# Step 1: Sanitize user input
sanitizer = Sanitizer()
user_input = "Found AWS key AKIAIOSFODNN7EXAMPLE in config"
sanitized = sanitizer.sanitize(user_input)

# Step 2: Create secure instruction
instruction = CloudInstruction(
    task_id="sec-001",
    action="analyze_smali",
    target="malware.apk",
    confidence=0.92,
    reasoning=sanitized.sanitized_text  # Use sanitized version!
)

print(f"Safe instruction: {instruction.reasoning}")
# Output: "Found AWS key [REDACTED] in config"
```

---

## 🏗️ Architecture


---

## 🛣️ Roadmap

### ✅ Phase 0: Foundation (Week 1) - COMPLETE
- [x] Pydantic schemas (CloudInstruction, SanitizedOutput)
- [x] Sanitizer component with regex detection
- [x] Unit tests (13 tests, 100% coverage on core)
- [x] Integration tests (6 tests)
- [x] Pre-commit hooks (ruff, bandit, pytest)

### 📋 Phase 1: Multi-Agent System (Week 2)
- [ ] Architect agent (system design)
- [ ] Developer agent (code generation)
- [ ] Tester agent (QA validation)
- [ ] CrewAI orchestration
- [ ] Agent communication protocol

### 📋 Phase 2: Security Tools (Week 3)
- [ ] Smali analyzer
- [ ] Web reconnaissance module
- [ ] CVE validator
- [ ] Cloud provider integrations (AWS/Azure/GCP)

### 📋 Phase 3: Reporting & Deployment (Week 4)
- [ ] Security report generator
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Documentation site

---

## 🔒 Security Principles

1. **Defense in Depth**
   - Multiple validation layers (Sanitizer → Schema validators)
   - Fail-secure by default

2. **Zero Trust**
   - All user input sanitized before processing
   - No secrets in logs or outputs

3. **Least Privilege**
   - Agent instructions restricted to specific actions
   - Confidence thresholds enforced

---

## 🧪 Development

### Running Tests

```bash
# All tests with coverage
pytest --cov=daqiq --cov-report=term-missing

# Specific test file
pytest tests/unit/test_sanitizer.py -v

# Watch mode (with pytest-watch)
ptw
```

### Code Quality

```bash
# Run linters
ruff check .
ruff format .

# Security scan
bandit -r daqiq/

# Type checking (future)
mypy daqiq/
```

### Pre-commit Hooks

Installed automatically on first commit:
- **ruff**: Code formatting and linting
- **bandit**: Security vulnerability scanning  
- **pytest**: All tests must pass with 80% coverage

---

## 📚 Documentation

- **API Reference:** [Coming in Week 4]
- **Architecture Guide:** [DAQIQ_MASTER_PLAN.md](DAQIQ_MASTER_PLAN.md)
- **Agent Memory:** [AGENT_MEMORY.md](AGENT_MEMORY.md)

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for new functionality
4. Ensure all tests pass (`pytest`)
5. Commit changes (`git commit -m 'feat: add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open Pull Request

---

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 🙏 Acknowledgments

- **Pydantic** - Data validation framework
- **Ollama** - Local LLM inference
- **CrewAI** - Multi-agent orchestration
- **Ruff** - Fast Python linter

---

## 📧 Contact

**Project Maintainer:** Moaid EL-Moatasem Bellah  
**Status:** Phase 0 Complete (Week 1) ✅

---

**Built with ❤️ for secure AI-powered security testing**


## 🤖 Autonomous Agent System

DAQIQ now includes a fully autonomous development system built by AI agents!

### Quick Start

Run an autonomous security workflow:
```bash
cd daqiq-dev-agents
python daqiq-professional/scripts/demo_workflow_execution.py
```

See [AUTONOMOUS_SYSTEM_README.md](daqiq-professional/AUTONOMOUS_SYSTEM_README.md) for full documentation.

### Features

- ✅ Self-managing development
- ✅ YAML-based workflow orchestration  
- ✅ Autonomous decision-making
- ✅ Zero manual coding required
- ✅ Production-ready in 38 minutes

### Statistics

- 🤖 28 agents deployed
- 📝 900+ lines generated
- ✅ 100% test coverage
- ⏱️ 7 autonomous iterations

Built entirely by MicroGPT swarm 🚀

---

## 📚 Documentation & Roadmap

- **[Complete Project Documentation](./daqiq-professional/MASTER_DOCUMENTATION.md)** - Technical details, status, metrics
- **[DAQIQ NEXUS v4 Roadmap](./docs/roadmap/DAQIQ_NEXUS_v4.md)** - Strategic plan, Phases 0-6, MiniGPT & RAG architecture
- **[Architecture Overview](./docs/architecture/overview.md)** - Dual-brain system design

---

## 📋 Open Source Roadmap

DAQIQ is evolving through 6 phases:

| Phase | Focus | Status | Timeline |
|-------|-------|--------|----------|
| **0-1** | Foundation + Zero-Trust Core | 🔄 In Progress | Now (0-3 mo) |
| **2-3** | RAG + Burhan + Dynamic Analysis | 📅 Planned | Q3 2026 (3-9 mo) |
| **4-5** | Defense + Forensic UI | 📅 Planned | Q4 2026 (9-18 mo) |
| **6** | Cairo Pilot + Open-Core | 📅 Planned | 2027 (19-24 mo) |

**Current Status**:
- ✅ 132 autonomous scanners (Layer 1 - Execution)
- 🔄 Sanitization Bridge (91.78% coverage)
- 🔄 Hardware-agnostic design (x86_64, ARM64, Cloud)
- 📅 Daqiq Trace + Burhan validation (Layer 2 - Intelligence)

See **[Full Roadmap](./docs/roadmap/DAQIQ_NEXUS_v4.md)** for details.

---

## 📜 License

**MIT License** - see [LICENSE](./LICENSE) for details.

Copyright (c) 2026 Moaid EL-Moatasem Bellah

---

## 🤝 Contributing

DAQIQ is open source! Contributions welcome:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Guidelines**:
- Maintain ≥80% test coverage for new code
- Follow existing code style (Ruff + Bandit)
- Update documentation for new features
- Security-sensitive changes require manual review

---

## 🔒 Security

For security vulnerabilities, see [SECURITY.md](./SECURITY.md).

**Security Principles**:
- Zero-trust sanitization (all inputs sanitized)
- Stateless MiniGPTs (no session memory)
- Fail-closed architecture (reject unsafe operations)
- Hardware-agnostic deployment (no vendor lock-in)

---

## 📞 Contact

- **Project Lead**: Moaid EL-Moatasem Bellah
- **Repository**: [github.com/moaidmoatasem/daqiq-professional](https://github.com/moaidmoatasem/daqiq-professional)
- **Issues**: [GitHub Issues](https://github.com/moaidmoatasem/daqiq-professional/issues)

---

**Built with ❤️ for secure AI-powered security testing**  
*Hardware-Agnostic | Open Source | Zero-Trust by Design*
