#!/usr/bin/env python3
"""
CHERENKOV — GitHub Issues & Project Board Setup Script
Automates the creation of milestones, labels, and issues on GitHub.
Requires: gh CLI installed and authenticated (run 'gh auth login' first).
"""

import sys
import subprocess
import shutil

def run_command(cmd, shell=False):
    try:
        res = subprocess.run(cmd, shell=shell, text=True, capture_output=True, check=True)
        return res.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command {cmd}: {e.stderr}")
        return None

def main():
    print("==========================================================")
    print("[+] Initializing Cherenkov GitHub Project Infrastructure...")
    print("==========================================================")

    # 1. Check for gh CLI
    if not shutil.which("gh"):
        print("ERROR: GitHub CLI ('gh') is not installed or not in PATH.")
        print("       Please install it using: sudo apt install gh")
        sys.exit(1)

    # 2. Check for gh auth
    auth_status = run_command(["gh", "auth", "status"])
    if not auth_status:
        print("ERROR: GitHub CLI is not authenticated.")
        print("       Please run 'gh auth login' first.")
        sys.exit(1)

    print("--> Creating customized project labels...")
    run_command(["gh", "label", "create", "performance", "--color", "3B82F6", "--description", "Metrics, TTFT, and load benchmarks", "--force"])
    run_command(["gh", "label", "create", "quantization", "--color", "F59E0B", "--description", "INT4 model compression and caching", "--force"])
    run_command(["gh", "label", "create", "deployment", "--color", "10B981", "--description", "vLLM and Docker ecosystem setups", "--force"])
    run_command(["gh", "label", "create", "testing", "--color", "8B5CF6", "--description", "CI/CD and integration test suite checks", "--force"])

    print("--> Registering Milestone: 'vLLM Sovereign Transition'...")
    # Attempt to create milestone via API or CLI
    # (Note: Using gh api command to handle robust creation)
    gh_api_cmd = [
        "gh", "api", "repos/:owner/:repo/milestones",
        "-f", "title=vLLM Sovereign Transition",
        "-f", "description=Milestone for transitioning Cherenkov from Ollama to high-throughput quantized vLLM servers."
    ]
    run_command(gh_api_cmd)

    print("--> Generating Issue 1: Ollama Baseline Benchmarking...")
    issue1_body = (
        "### Description\n"
        "Before migrating Cherenkov's sovereign scanner swarm from Ollama to vLLM, "
        "we need to establish a precise, repeatable performance baseline (the control group) under realistic workloads.\n\n"
        "### Tasks\n"
        "- [ ] Ensure Ollama is running and has the `qwen2.5-coder:7b` model loaded.\n"
        "- [ ] Run the load-test emulator with 5 concurrent agents for 60 seconds:\n"
        "  ```bash\n"
        "  bash scripts/benchmark_ollama.sh 5 60\n"
        "  ```\n"
        "- [ ] Assert that the test completes successfully and outputs a JSON baseline in the `benchmarks/` directory.\n"
        "- [ ] Record baseline statistics (throughput in requests/sec, TTFT, and latency) in `docs/ROADMAP.md` or a wiki.\n\n"
        "### Acceptance Criteria\n"
        "- A clean, parsed benchmark JSON is saved in `benchmarks/`."
    )
    run_command([
        "gh", "issue", "create",
        "--title", "task: Establish multi-agent inference performance baseline using Ollama",
        "--body", issue1_body,
        "--label", "performance,testing",
        "--milestone", "vLLM Sovereign Transition"
    ])

    print("--> Generating Issue 2: Connected Caching Phase...")
    issue2_body = (
        "### Description\n"
        "Set up the local directory footprint for offline model compression. This is the internet-connected "
        "Phase A download step that caches base weights and code domain calibration files on a local disk "
        "before moving to air-gapped environments.\n\n"
        "### Tasks\n"
        "- [ ] Activate virtual environment and install requirements:\n"
        "  ```bash\n"
        "  pip install openai transformers datasets llmcompressor guidellm\n"
        "  ```\n"
        "- [ ] Run the download phase:\n"
        "  ```bash\n"
        "  python3 scripts/quantize_tensor.py --phase download\n"
        "  ```\n"
        "- [ ] Verify that model weights are fully saved in `models/downloads/qwen2.5-coder-7b/` (~14 GB).\n"
        "- [ ] Verify that the Python calibration dataset is saved in `models/downloads/calibration_dataset/`.\n\n"
        "### Acceptance Criteria\n"
        "- Complete base weights and tokenizers are saved locally and are offline-accessible."
    )
    run_command([
        "gh", "issue", "create",
        "--title", "task: Run Phase A model caching and calibration dataset download",
        "--body", issue2_body,
        "--label", "quantization",
        "--milestone", "vLLM Sovereign Transition"
    ])

    print("--> Generating Issue 3: Local Quantization Execution...")
    issue3_body = (
        "### Description\n"
        "Apply 4-bit GPTQ quantization to the cached `Qwen2.5-Coder-7B` model using Neural Magic's modern `llmcompressor` modifier library.\n\n"
        "### Tasks\n"
        "- [ ] Run Phase B quantization utilizing the cached offline calibration files:\n"
        "  ```bash\n"
        "  python3 scripts/quantize_tensor.py --phase quantize --local\n"
        "  ```\n"
        "- [ ] Verify that VRAM-saving metrics (e.g. CPU offloading) activate correctly if GPU VRAM is <10 GB.\n"
        "- [ ] Confirm output safetensors occupy ~4.5 GB in `models/qwen2.5-coder-7b-int4-w4a16/`.\n"
        "- [ ] Run the unified integration test suite targeting the local quantized files:\n"
        "  ```bash\n"
        "  python3 tests/test_integration.py\n"
        "  ```\n\n"
        "### Acceptance Criteria\n"
        "- Model sizes occupy less than 5 GB of disk space.\n"
        "- Integration tests assert that the model retains its code-domain vulnerability reasoning precision."
    )
    run_command([
        "gh", "issue", "create",
        "--title", "task: Execute local code-focused INT4 quantization via llmcompressor",
        "--body", issue3_body,
        "--label", "quantization,testing",
        "--milestone", "vLLM Sovereign Transition"
    ])

    print("--> Generating Issue 4: vLLM Server Migration...")
    issue4_body = (
        "### Description\n"
        "Migrate inference from Ollama to a dedicated high-concurrency vLLM server. Leverage PagedAttention to maximize scanner throughput.\n\n"
        "### Tasks\n"
        "- [ ] Install vLLM on the GPU host.\n"
        "- [ ] Spin up the API server with the quantized weights:\n"
        "  ```bash\n"
        "  python3 -m vllm.entrypoints.openai.api_server \\\n"
        "    --model ./models/qwen2.5-coder-7b-int4-w4a16 \\\n"
        "    --gpu-memory-utilization 0.75 \\\n"
        "    --max-model-len 8192 \\\n"
        "    --port 8080\n"
        "  ```\n"
        "- [ ] Update `UnifiedLLMClient` configurations to point to vLLM (port 8080).\n"
        "- [ ] Run E2E swarm agent runner and verify throughput boosts:\n"
        "  ```bash\n"
        "  python3 src/agent_runner.py vllm /home/moaid/cherenkov-professional/models/qwen2.5-coder-7b-int4-w4a16\n"
        "  ```"
    )
    run_command([
        "gh", "issue", "create",
        "--title", "task: Deploy quantized weights on vLLM server and hot-swap inference API",
        "--body", issue4_body,
        "--label", "deployment",
        "--milestone", "vLLM Sovereign Transition"
    ])

    print("==========================================================")
    print("[✔] Success: GitHub Milestones, Labels, and Issues are set up!")
    print("    View your repository board to manage these tasks.")
    print("==========================================================")

if __name__ == "__main__":
    main()
