#!/bin/bash
# Task #237: Scan result aggregation pipeline
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
cd /home/moaid/cherenkov-professional

git checkout main
git checkout -b feat/237-aggregator 2>/dev/null || git checkout feat/237-aggregator

aider --model ollama_chat/qwen2.5-coder:7b --edit-format diff --yes \
  --message "Create packages/cherenkov/core/aggregator.py with class ScanAggregator. Method aggregate(results: list of ScanResult) returns ScanResult. Merge findings from N parallel scanner results into one unified ScanResult. Deduplicate findings by target plus scanner_name plus finding title. Sort findings by severity with CRITICAL first then HIGH MEDIUM LOW INFO. Sum duration_ms from all results. Keep highest severity when deduplicating. Merged ScanResult uses target from first result and scanner_name equals aggregated. Also create tests/unit/test_aggregator.py with test_aggregator_merges and test_aggregator_empty and test_aggregator_severity_sort. Import from cherenkov.core.base_scanner import ScanResult Finding Severity." \
  packages/cherenkov/core/base_scanner.py

# Commit
ruff format packages/ 2>/dev/null || true
git add -A
git commit -m "feat(core): scan result aggregation pipeline (#237)

Closes #237
Co-Authored-By: Aider+Ollama <noreply@local>" || echo "Nothing to commit"
echo "TASK 237 DONE"
