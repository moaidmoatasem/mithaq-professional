# CHERENKOV · GitHub Tasks & Project Board Setup Guide

This document lists the structured **GitHub Issues** and provides a ready-to-run **GitHub CLI Setup Script** to populate your repository's task board. These issues are fully aligned with the Cherenkov sovereign transition roadmap.

---

## 1. Structured GitHub Issues

### Issue #1: [Phase 1] Establish Multi-Agent Ollama Performance Baseline
* **Title:** `task: Establish multi-agent inference performance baseline using Ollama`
* **Labels:** `performance`, `testing`, `baseline`
* **Assignee:** `@moaid` (or active agent)
* **Description:**
  ```markdown
  ### Description
  Before migrating Cherenkov's sovereign scanner swarm from Ollama to vLLM, we need to establish a precise, repeatable performance baseline (the control group) under realistic workloads.

  ### Tasks
  - [ ] Ensure Ollama is running and has the `qwen2.5-coder:7b` model loaded.
  - [ ] Run the load-test emulator with 5 concurrent agents for 60 seconds:
    ```bash
    bash scripts/benchmark_ollama.sh 5 60
    ```
  - [ ] Assert that the test completes successfully and outputs a JSON baseline in the `benchmarks/` directory.
  - [ ] Record baseline statistics (throughput in requests/sec, TTFT, and latency) in `docs/ROADMAP.md` or a wiki.

  ### Acceptance Criteria
  - A clean, parsed benchmark JSON is saved in `benchmarks/`.
  - Verification that the local Ollama instance can handle the `micro_swarm` workload without timing out.
  ```

---

### Issue #2: [Phase 2] Download Model and Calibration Dataset for W4A16 Quantization
* **Title:** `task: Run Phase A model caching and calibration dataset download`
* **Labels:** `quantization`, `data-prep`
* **Assignee:** `@moaid` (or active agent)
* **Description:**
  ```markdown
  ### Description
  Set up the local directory footprint for offline model compression. This is the internet-connected "Phase A" download step that caches base weights and code domain calibration files on a local disk before moving to air-gapped environments.

  ### Tasks
  - [ ] Activate virtual environment and install requirements:
    ```bash
    pip install openai transformers datasets llmcompressor guidellm
    ```
  - [ ] Run the download phase:
    ```bash
    python3 scripts/quantize_tensor.py --phase download
    ```
  - [ ] Verify that model weights are fully saved in `models/downloads/qwen2.5-coder-7b/` (~14 GB).
  - [ ] Verify that the Python calibration dataset is saved in `models/downloads/calibration_dataset/`.

  ### Acceptance Criteria
  - Complete base weights and tokenizers are saved locally and are offline-accessible.
  ```

---

### Issue #3: [Phase 3] Run Local W4A16 GPTQ Quantization
* **Title:** `task: Execute local code-focused INT4 quantization via llmcompressor`
* **Labels:** `quantization`, `optimization`
* **Description:**
  ```markdown
  ### Description
  Apply 4-bit GPTQ quantization to the cached `Qwen2.5-Coder-7B` model using Neural Magic's modern `llmcompressor` modifier library.

  ### Tasks
  - [ ] Run Phase B quantization utilizing the cached offline calibration files:
    ```bash
    python3 scripts/quantize_tensor.py --phase quantize --local
    ```
  - [ ] Verify that VRAM-saving metrics (e.g. CPU offloading) activate correctly if GPU VRAM is <10 GB.
  - [ ] Confirm output safetensors occupy ~4.5 GB in `models/qwen2.5-coder-7b-int4-w4a16/`.
  - [ ] Run the unified integration test suite targeting the local quantized files:
    ```bash
    python3 tests/test_integration.py
    ```

  ### Acceptance Criteria
  - Model sizes occupy less than 5 GB of disk space.
  - Integration tests assert that the model retains its code-domain vulnerability reasoning precision.
  ```

---

### Issue #4: [Phase 4] Migrate Production Endpoint to vLLM Server
* **Title:** `task: Deploy quantized weights on vLLM server and hot-swap inference API`
* **Labels:** `deployment`, `vllm`, `infrastructure`
* **Description:**
  ```markdown
  ### Description
  Migrate inference from Ollama to a dedicated high-concurrency vLLM server. Leverage PagedAttention to maximize scanner throughput.

  ### Tasks
  - [ ] Install vLLM on the GPU host.
  - [ ] Spin up the API server with the quantized weights:
    ```bash
    python3 -m vllm.entrypoints.openai.api_server \
      --model ./models/qwen2.5-coder-7b-int4-w4a16 \
      --gpu-memory-utilization 0.75 \
      --max-model-len 8192 \
      --port 8080
    ```
  - [ ] Update `UnifiedLLMClient` configurations to point to vLLM (port 8080).
  - [ ] Run E2E swarm agent runner and verify throughput boosts:
    ```bash
    python3 src/agent_runner.py vllm /home/moaid/cherenkov-professional/models/qwen2.5-coder-7b-int4-w4a16
    ```
  ```

---

## 2. GitHub CLI Automation Script

You (or any active agent operating inside your WSL shell) can run the script below to automatically initialize these issues in GitHub.

See **[`scripts/setup_github.py`](file:///home/moaid/cherenkov-professional/scripts/setup_github.py)**.
