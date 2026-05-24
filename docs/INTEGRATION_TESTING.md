# CHERENKOV · Integration Testing & Verification Guide

This guide describes how to run, verify, and audit the Cherenkov multi-agent security inference pipeline. It ensures absolute compatibility and performance verification across Ollama and vLLM backends.

---

## 1. Environment Prerequisites

Before running the integration tests or the agent swarm, ensure that all required dependencies are installed inside your WSL Ubuntu-24.04 shell:

```bash
# 1. Update system package index
sudo apt-get update && sudo apt-get install -y python3-pip python3-venv curl

# 2. Set up a virtual environment inside your workspace
cd /home/moaid/cherenkov-professional
python3 -m venv .venv
source .venv/bin/activate

# 3. Install core dependencies
pip install --upgrade pip
pip install openai transformers datasets llmcompressor guidellm
```

---

## 2. Verification Pipelines

### 🧪 Pipeline 1: Automated Integration Tests
The integration test suite validates connection reliability, model prompt templates, and core security reasoning capabilities.

```bash
# Run the test suite (defaults to Ollama)
python3 tests/test_integration.py
```

* **What it validates:**
  1. Client initialization parameters.
  2. Endpoint connection connectivity.
  3. Security reasoning validation (verifies that the model correctly identifies SQL Injection in unsafe inputs).
  4. Performance metrics collection (aggregates prompt latency and generation throughput).

* **How to retarget for vLLM:**
  Edit the class variables in `tests/test_integration.py` (`setUpClass` method):
  ```python
  cls.backend = "vllm"
  cls.model_name = "/home/moaid/cherenkov-professional/models/qwen2.5-coder-7b-int4-w4a16"
  ```

---

### 🤖 Pipeline 2: Runnable Multi-Agent Swarm Simulation
Runs an end-to-end simulated audit flow using sequential scanning and compliance reporting agents.

```bash
# Execute simulation using Ollama baseline
python3 src/agent_runner.py ollama qwen2.5-coder:7b

# Execute simulation using local quantized vLLM server
python3 src/agent_runner.py vllm /home/moaid/cherenkov-professional/models/qwen2.5-coder-7b-int4-w4a16
```

* **Workflow Execution Steps:**
  1. **TENSOR Agent** scans a mock Flask codebase looking for hardcoded passwords, SQL Injection, and command execution flaws.
  2. **KINETIC Agent** parses the technical findings, triages the severity, and outputs a formatted compliance executive report.
  3. **Metrics Logger** prints the total request latency, tokens generated, and average generation throughput (tokens/sec).

---

### 📈 Pipeline 3: Multi-Agent Load-Testing Benchmark
Simulates heavy parallel agent workloads against the running server.

```bash
# Run the load-tester (5 concurrent agents for 60 seconds)
bash scripts/benchmark_ollama.sh 5 60
```

* **Output Analysis:**
  Check `benchmarks/ollama-tensor-baseline-*.json`. Record:
  * `requests_per_second`: Average scan request throughput.
  * `p50_time_to_first_token_ms`: Agent responsiveness.
  * `p99_inter_token_latency_ms`: Response generation smoothness.

---

## 3. Troubleshooting & Failure Recovery

### ❌ Issue 1: Connection Refused Error
```
ConnectionRefusedError: [Errno 111] Connection refused
```
* **Cause:** The backend server (Ollama or vLLM) is not running or is serving on a different port.
* **Resolution:**
  * For Ollama: Verify the service status by running `curl http://localhost:11434/v1/models`. If offline, start it using `ollama serve`.
  * For vLLM: Verify that the server started successfully on port `8080` and has not crashed due to OOM.

### ❌ Issue 2: CUDA Out of Memory (OOM)
```
torch.OutOfMemoryError: CUDA out of memory.
```
* **Cause:** The model is too large for the GPU VRAM, or multiple processes are hogging GPU resources.
* **Resolution:**
  * When quantizing, the script will automatically enable `cpu_offload` if total VRAM is <10 GB.
  * When serving the quantized model via vLLM, restrict VRAM allocation to leave headroom for KV Caching:
    ```bash
    python3 -m vllm.entrypoints.openai.api_server \
      --model ./models/qwen2.5-coder-7b-int4-w4a16 \
      --gpu-memory-utilization 0.75
    ```

### ❌ Issue 3: WSL Lacks GPU Access
```
UserWarning: CUDA initialization: CUDA unknown error
```
* **Cause:** NVIDIA drivers or CUDA toolkit are missing inside the WSL environment.
* **Resolution:**
  1. Install the latest official **NVIDIA Windows Display Driver** on the host. WSL automatically inherits host GPU access.
  2. Install the **CUDA Toolkit for WSL** inside Ubuntu:
     ```bash
     sudo apt-get install -y cuda-toolkit
     ```
  3. Verify access using: `nvidia-smi` inside WSL.
