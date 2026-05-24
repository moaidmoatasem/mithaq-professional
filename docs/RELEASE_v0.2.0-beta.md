# CHERENKOV · Release v0.2.0-beta

Welcome to the **v0.2.0-beta** release of the **Cherenkov Sovereign Security Platform**! 

This release lays the baseline testing, E2E multi-agent execution client, and quantization pipeline for our transition to the high-throughput, GPU-optimized **vLLM** ecosystem. It introduces a highly reliable client layer, a runnable E2E simulation harness, and automated integration tests supporting mock operations for headless CI runners.

---

## 🚀 Key Features & Architectural Upgrades

### 1. Unified Pluggable Inference Interface
We have introduced **`UnifiedLLMClient`** (`src/vllm_client.py`), an OpenAI-compatible client wrapper that acts as the single entry point for all agent inference.
* Supports seamless hot-swapping between the **Ollama** control baseline (port 11434) and the upcoming **vLLM** server (port 8080).
* Built-in exponential backoff retry algorithms to guarantee scan resilience when the inference server is heavily loaded.
* Detailed token consumption logging and latency tracking metrics.

### 2. Multi-Agent Scan Simulation (Runnable Sandbox)
A runnable end-to-end security audit workspace is now live via **`src/agent_runner.py`**.
* **Static Analysis Agent (TENSOR)**: Audits Flask web applications looking for SQL Injection, Command Execution, and hardcoded credentials.
* **Triage & Reporting Agent (KINETIC)**: Takes technical findings and compiles formatted, compliant Executive Security Reports.
* Prints real-time token generation throughput metrics (tokens/sec).

### 3. Automated Integration Test Suite & CI/CD
Automated pipeline tests are now live in **`tests/test_integration.py`**.
* Checks client-endpoint connectivity, checks model loading correctness, and asserts security reasoning quality.
* **Mock CI Integration**: Supports the environment flag `CI=true` to dynamically mock chat completions. This allows our **GitHub Actions Integration Pipeline** (`.github/workflows/ci.yml`) to pass style-linting and code assertions on every commit without needing a live CUDA/WSL host in the headless runner.

### 4. Precision-Calibrated Quantization Script
The download and quantization script **`scripts/quantize_tensor.py`** is prepared for local compression of the TENSOR (Qwen-7B) model.
* Utilizes Modern class-based `GPTQModifier` modifiers to avoid serialization bugs.
* Calibrates weights specifically on code repositories (`codeparrot/github-code`) to prevent accuracy degradation in security-scanning capability.

---

## 📝 Changelog

### Added:
- Added `src/vllm_client.py` unified OpenAI-compatible client interface.
- Added `src/agent_runner.py` runnable multi-agent scanning simulation workflow.
- Added `tests/test_integration.py` automated integration test suite with CI mocking functionality.
- Added `.github/workflows/ci.yml` GitHub Actions pipeline automation.
- Added `docs/ROADMAP.md` high-level technical architecture and milestones roadmap.
- Added `docs/INTEGRATION_TESTING.md` installation and test verification guide.
- Added `docs/GITHUB_TASKS.md` structured issue checklist and board tracking guide.
- Added `docs/RELEASE_v0.2.0-beta.md` changelog draft.
- Added `scripts/setup_github.py` script to automatically populate repository labels, milestones, and issues using the GitHub CLI (`gh`).

---

## 📦 Getting Started & Commands

To set up the v0.2.0-beta dependencies inside your WSL shell and execute the verification tests, run:

```bash
# Setup environment
python3 -m venv .venv
source .venv/bin/activate
pip install openai transformers datasets llmcompressor guidellm

# Execute automated tests (Ollama must be serving local Qwen)
python3 tests/test_integration.py

# Run E2E simulated agent audit
python3 src/agent_runner.py ollama qwen2.5-coder:7b
```
