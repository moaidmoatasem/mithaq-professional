#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════
# CHERENKOV — Aider Local Agent Task Runner
# Model: qwen2.5-coder:7b via Ollama (fully local, $0 cost)
# Usage: ./scripts/aider-tasks.sh [task-number|help]
# ═══════════════════════════════════════════════════════════
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# ─── TASK 1: Root Cleanup (#223, P0) ────────────────────
# Git-only task, no AI needed. Moves stale files out of root.
run_task_1() {
  echo "═══ TASK 1: Root Cleanup — Issue #223 (P0) ═══"
  git checkout main
  git checkout -b fix/223-root-cleanup 2>/dev/null || git checkout fix/223-root-cleanup

  mkdir -p scripts/output archive tests/legacy

  # Move dev scripts
  for f in batch_scan.sh demo_complete_system.sh get-docker.sh monitor_perfection.sh \
           phase1_open_source.sh run_all_systems.sh run_all_systems.ps1 \
           run_autonomous_agent.sh setup.sh; do
    [ -f "$f" ] && git mv "$f" scripts/ 2>/dev/null && echo "  ✓ $f → scripts/"
  done

  # Move stale scan reports
  for f in scan_report_*.json; do
    [ -f "$f" ] && git mv "$f" scripts/output/ 2>/dev/null && echo "  ✓ $f → scripts/output/"
  done

  # Move legacy code
  for f in cherenkov_web.py cherenkov_simple_scanner.py cherenkov_cli.py \
           session_manager.py system_dashboard.py; do
    [ -f "$f" ] && git mv "$f" archive/ 2>/dev/null && echo "  ✓ $f → archive/"
  done

  # Move root test files
  for f in test_*.py; do
    [ -f "$f" ] && git mv "$f" tests/legacy/ 2>/dev/null && echo "  ✓ $f → tests/legacy/"
  done

  # Delete stale output
  for f in pytest_output.txt validation_results.json; do
    [ -f "$f" ] && git rm "$f" 2>/dev/null && echo "  ✗ deleted $f"
  done

  # Move stale output dirs
  [ -d "workflow_results" ] && git mv workflow_results archive/ 2>/dev/null && echo "  ✓ workflow_results/ → archive/"

  # Count remaining root items
  echo ""
  echo "Root items after cleanup: $(ls -1 | wc -l)"
  echo ""

  git add -A
  git commit -m "chore(infra): root directory cleanup — move stale artifacts (#223)

Closes #223
Co-Authored-By: Antigravity <noreply@google.com>"

  echo "✓ Task 1 complete. PR ready: git push -u origin fix/223-root-cleanup"
}

# ─── TASK 2: Real Health Metrics (#221, P0) ──────────────
# AI task — rewire /api/v1/health with real Ollama + Meissner state
run_task_2() {
  echo "═══ TASK 2: Real Health Metrics — Issue #221 (P0) ═══"
  git checkout main
  git checkout -b feat/221-real-health-metrics 2>/dev/null || git checkout feat/221-real-health-metrics

  aider \
    --message "Read the task spec in .agents/tasks/issue-221.md carefully.

Implement REAL health metrics in packages/cherenkov/api/main.py:

1. Add async _check_ollama() that does GET http://localhost:11434/api/tags with httpx (2s timeout). Return 'ready' or 'offline'.

2. In v1_health() endpoint, replace hardcoded node statuses with real Ollama check results. Import meissner_hub from cherenkov.core.circuit_breaker and return its real state.

3. Add a startup time tracker: _start_time = time.time() at module level, return uptime in the health response.

4. Create tests/unit/test_api_health.py with:
   - test_health_meissner_state: mock _check_ollama to return 'offline', assert status='degraded' and meissner state is valid.
   - test_health_ollama_ready: mock _check_ollama to return 'ready', assert status='operational'.

Use httpx for the Ollama check. Follow existing import patterns. Run ruff format when done.

IMPORTANT: Do NOT modify any routes other than /api/v1/health. Do NOT touch auth middleware." \
    packages/cherenkov/api/main.py \
    packages/cherenkov/core/circuit_breaker.py \
    .agents/tasks/issue-221.md

  echo "✓ Task 2 complete. Verify: pytest tests/unit/test_api_health.py -v"
}

# ─── TASK 3: Graduate Scanners (#178, P1) ────────────────
# AI task — promote 3 autonomous scanners to BaseScanner contract
run_task_3() {
  echo "═══ TASK 3: Graduate Scanners — Issue #178 (P1) ═══"
  git checkout main
  git checkout -b feat/178-graduate-scanners 2>/dev/null || git checkout feat/178-graduate-scanners

  aider \
    --message "Read .agents/tasks/issue-178.md for the full spec.

Graduate these 3 scanners from packages/cherenkov/autonomous_generated/scanners/ to packages/cherenkov/scanners/:

1. xxe_scanner.py → XxeScanner
2. pathtraversalscanner.py → PathTraversalScanner (rename to path_traversal_scanner.py)
3. fileuploadscanner.py → FileUploadScanner (rename to file_upload_scanner.py)

For each:
- Rewrite to inherit BaseScanner from cherenkov.core.base_scanner
- Implement async scan(target, timeout) returning ScanResult
- Use self._http_request for all HTTP calls
- Register in packages/cherenkov/core/registry.py
- Create a test in tests/unit/ following the pattern in .agents/tasks/issue-178.md

Follow snake_case file naming. Run ruff format when done." \
    packages/cherenkov/core/base_scanner.py \
    packages/cherenkov/core/registry.py \
    packages/cherenkov/autonomous_generated/scanners/xxe_scanner.py \
    packages/cherenkov/autonomous_generated/scanners/pathtraversalscanner.py \
    packages/cherenkov/autonomous_generated/scanners/fileuploadscanner.py \
    .agents/tasks/issue-178.md

  echo "✓ Task 3 complete. Verify: pytest tests/unit/test_*scanner* -v"
}

# ─── TASK 4: Merge fix branch → main ────────────────────
# Git-only — merge the current working branch
run_task_4() {
  echo "═══ TASK 4: Merge fix/missing-deps-and-icon → main ═══"
  git checkout main
  git merge fix/missing-deps-and-icon --no-edit || {
    echo "⚠ Merge conflict — resolve manually: git mergetool"
    return 1
  }
  echo "✓ Merged to main. Run: pytest -m 'not (integration or ai_generated)' --tb=short"
}

# ─── TASK 5: Decision Hub tests boost ────────────────────
# AI task — fill in test coverage for the new DecisionHub agent
run_task_5() {
  echo "═══ TASK 5: DecisionHub Test Coverage ═══"
  git checkout main
  git checkout -b test/decision-hub-coverage 2>/dev/null || git checkout test/decision-hub-coverage

  aider \
    --message "Expand tests/unit/test_decision_hub.py to achieve comprehensive coverage of packages/cherenkov/agents/decision_hub.py.

Add tests for:
1. All public methods — especially approve/reject flows
2. Edge cases: empty findings list, None target, duplicate finding IDs
3. Error paths: network failures, invalid states
4. Mock all external dependencies (DB, API calls)
5. Use pytest fixtures for common setup

Keep existing tests, only add new ones. Use pytest.mark.asyncio for async tests.
Run ruff format when done." \
    packages/cherenkov/agents/decision_hub.py \
    tests/unit/test_decision_hub.py

  echo "✓ Task 5 complete. Verify: pytest tests/unit/test_decision_hub.py -v"
}

# ─── TASK 6: Frontend HITL polish ────────────────────────
# AI task — polish PendingApprovalsPanel + ForensicHeader badge
run_task_6() {
  echo "═══ TASK 6: HITL Approval Panel Polish (Frontend) ═══"
  git checkout main
  git checkout -b feat/web-hitl-polish 2>/dev/null || git checkout feat/web-hitl-polish

  aider \
    --message "Polish the HITL approval UI in these two files:

ForensicHeader.tsx:
1. Add a pulsing CSS animation on the pending approvals badge when count > 0
2. Add aria-label for accessibility
3. Badge should glow amber when count > 5

PendingApprovalsPanel.tsx:
1. Add severity-colored left border to each finding card (CRITICAL=red, HIGH=orange, MEDIUM=yellow, LOW=green)
2. Add a confirmation step before rejecting a finding
3. Improve the empty-state message

Use the existing design tokens and CyberBadge/CyberButton atoms.
Import patterns: @/src/lib/, @/src/hooks/, @/src/components/atoms/.
Do NOT change any API calls or data fetching logic." \
    packages/cherenkov/web/src/components/organisms/ForensicHeader.tsx \
    packages/cherenkov/web/src/components/organisms/PendingApprovalsPanel.tsx

  echo "✓ Task 6 complete. Verify: cd packages/cherenkov/web && npx tsc --noEmit"
}

# ─── DISPATCHER ──────────────────────────────────────────
case "${1:-help}" in
  1) run_task_1 ;;
  2) run_task_2 ;;
  3) run_task_3 ;;
  4) run_task_4 ;;
  5) run_task_5 ;;
  6) run_task_6 ;;
  help|*)
    cat <<'EOF'

  ╔══════════════════════════════════════════════════════════╗
  ║     CHERENKOV — Local Agent Task Runner (Aider+Ollama)  ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                         ║
  ║  🔴 P0 PRIORITY                                         ║
  ║    1  Root cleanup (#223)           [git-only]          ║
  ║    2  Real health metrics (#221)    [AI — backend]      ║
  ║    4  Merge fix branch → main       [git-only]          ║
  ║                                                         ║
  ║  🟡 P1 PRIORITY                                         ║
  ║    3  Graduate scanners (#178)      [AI — backend]      ║
  ║    5  DecisionHub test coverage     [AI — tests]        ║
  ║    6  HITL panel polish             [AI — frontend]     ║
  ║                                                         ║
  ║  Usage:                                                 ║
  ║    ./scripts/aider-tasks.sh 1    # run task 1           ║
  ║    ./scripts/aider-tasks.sh help # show this menu       ║
  ║                                                         ║
  ║  Model: qwen2.5-coder:7b (Ollama) — $0 cost            ║
  ║  Config: .aider.conf.yml                                ║
  ╚══════════════════════════════════════════════════════════╝

EOF
    ;;
esac
