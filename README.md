
# 🛡️ DAQIQ - AI Security Framework

<!-- Auto-updated badges -->
![Version](https://img.shields.io/badge/version-v0.1.0--alpha-blue)
![Features](https://img.shields.io/badge/features-45-green)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Zero-trust AI security framework with local-first execution, PII redaction, and vulnerability scanning.

---

## 🚀 Quick Start (Docker)

```bash
# 1. Clone the repository
git clone https://github.com/moaidmoatasem/daqiq-professional.git
cd daqiq-professional

# 2. Start with Docker Compose (recommended)
docker-compose up -d

# 3. Verify installation
curl http://localhost:8000/health

# 4. Run your first scan
docker exec -it daqiq-professional-daqiq-1 python -m daqiq.cli scan --target example.com
```

---

## 📦 Installation Methods

### Method 1: Docker (Recommended)
```bash
docker pull moaidmoatasem/daqiq:latest
docker run -p 8000:8000 moaidmoatasem/daqiq:latest
```

### Method 2: Docker Compose
```bash
curl -O https://raw.githubusercontent.com/moaidmoatasem/daqiq-professional/main/docker-compose.yml
docker-compose up -d
```

### Method 3: From Source
```bash
git clone https://github.com/moaidmoatasem/daqiq-professional.git
cd daqiq-professional
pip install -r requirements.txt
python -m daqiq.main
```

---

## ✨ Features

### 🔒 Security
- **PII Redaction**: Automatically detect and redact sensitive data
- **Secret Scanning**: Find exposed API keys, passwords, tokens
- **Input Sanitization**: Zero-trust validation for all inputs
- **Vulnerability Scanning**: Detect security issues in code

### 🤖 AI Integration
- **Local-First**: tinyllama model (8.47s, 637MB) for <8GB RAM systems
- **CrewAI Orchestration**: Multi-agent AI workflows
- **Ollama Support**: Compatible with 6+ local models

### 🛠️ Developer Tools
- **80% Test Coverage**: Comprehensive pytest suite
- **Pre-commit Hooks**: Automated linting (ruff, bandit)
- **CI/CD Ready**: GitHub Actions workflows
- **Docker Support**: Multi-stage optimized builds

---

## 📊 Benchmarks

| Model | Speed | RAM | Status |
|-------|-------|-----|--------|
| tinyllama | 8.47s | 637MB | ✅ Default |
| qwen2.5-coder:3b | 97.98s | 2.1GB | ⚠️ Slow |
| Larger models | >120s | >4GB | ❌ Timeout |

---

## 🔧 Configuration

Create `.env`:
```bash
OLLAMA_MODEL=tinyllama
REDIS_HOST=localhost
REDIS_PORT=6379
LOG_LEVEL=INFO
```

---

## 📖 Documentation

- [Installation Guide](docs/installation.md)
- [Hardware Requirements](docs/hardware_requirements.md)
- [API Reference](docs/api.md)
- [Contributing](CONTRIBUTING.md)

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

<!-- Auto-updated release notes -->
## 📝 Latest Release

**v0.1.0-alpha** - Initial public release
- Model benchmarking complete
- tinyllama as default model
- 50+ security vulnerabilities fixed
- Production-ready infrastructure

[View all releases](https://github.com/moaidmoatasem/daqiq-professional/releases)
