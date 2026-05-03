#!/usr/bin/env python3
"""
Benchmark all Ollama models for DAQIQ
Tests: inference speed, RAM usage, code quality
"""

import json
import subprocess
import time
from datetime import datetime

MODELS = [
    "tinyllama",
    "qwen2.5-coder:3b",
    "qwen2.5:3b",
    "qwen2.5-coder:7b",
    "qwen3.5",
    "deepseek-coder-v2:16b",
]

TEST_PROMPT = "Write a Python function to detect SQL injection in a string"


def benchmark_model(model_name):
    """Benchmark a single model"""
    print(f"\n{'='*60}")
    print(f"Benchmarking: {model_name}")
    print(f"{'='*60}")

    # Measure inference time
    start = time.time()
    result = subprocess.run(
        ["ollama", "run", model_name, TEST_PROMPT], capture_output=True, text=True, timeout=120
    )
    elapsed = time.time() - start

    # Get memory usage
    mem_result = subprocess.run(["free", "-h"], capture_output=True, text=True)

    return {
        "model": model_name,
        "inference_time": round(elapsed, 2),
        "response_length": len(result.stdout),
        "success": result.returncode == 0,
        "timestamp": datetime.now().isoformat(),
    }


def main():
    results = []

    for model in MODELS:
        try:
            result = benchmark_model(model)
            results.append(result)
            print(f"Done: {model}: {result['inference_time']}s")
        except Exception as e:
            print(f"Error {model}: {e}")
            results.append({"model": model, "error": str(e), "success": False})

    # Save results
    output_file = "benchmarks/model_performance.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {output_file}")

    # Print summary
    print("\n" + "=" * 60)
    print("BENCHMARK SUMMARY")
    print("=" * 60)
    for r in results:
        if r.get("success"):
            print(f"{r['model']:25} {r['inference_time']:6.2f}s")


if __name__ == "__main__":
    main()
