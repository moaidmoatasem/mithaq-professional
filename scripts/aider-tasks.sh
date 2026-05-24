#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# CHERENKOV — Aider Task Runner (aligned to GitHub Issues #230–#247)
# Model: qwen2.5-coder:7b via Ollama | $0 cost | Fully local
# ═══════════════════════════════════════════════════════════════════
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# ─── HELPERS ─────────────────────────────────────────────
ensure_branch() {
  local branch="$1"
  git checkout main 2>/dev/null || true
  git checkout -b "$branch" 2>/dev/null || git checkout "$branch"
}

commit_and_report() {
  local issue="$1" msg="$2"
  ruff format packages/ 2>/dev/null || true
  ruff check packages/ --ignore W,S,B --fix 2>/dev/null || true
  git add -A
  git commit -m "$msg

Closes #$issue
Co-Authored-By: Aider+Ollama <noreply@local>" || echo "Nothing to commit"
  echo "✓ Done. Push: git push -u origin $(git branch --show-current)"
}

# ═══════════════════════════════════════════════════════════
# SPRINT 2 — v1.1.0 Milestone (Phase 2)
# ═══════════════════════════════════════════════════════════

# ─── #230 [CRITICAL] Remove cloud configs violating MEISSNER ──
run_230() {
  echo "═══ #230: Remove cloud deployment configs (MEISSNER) ═══"
  ensure_branch "fix/230-meissner-cloud-configs"

  mkdir -p archive/cloud-configs

  # Move Cloudflare Workers configs
  for f in wrangler.jsonc wrangler.toml; do
    [ -f "$f" ] && git mv "$f" archive/cloud-configs/ && echo "  → $f archived"
  done

  # Move root package.json if it's CF Workers only
  if [ -f package.json ] && grep -q "wrangler" package.json 2>/dev/null; then
    git mv package.json archive/cloud-configs/
    echo "  → package.json archived (CF Workers)"
  fi

  # Audit deploy/providers for cloud egress
  if [ -d deploy/providers ]; then
    git mv deploy/providers archive/cloud-configs/
    echo "  → deploy/providers/ archived"
  fi

  commit_and_report 230 "security(meissner): remove cloud deployment configs violating zero-egress invariant (#230)"
}

# ─── #232 [MEDIUM] Root directory cleanup ─────────────────
run_232() {
  echo "═══ #232: Root directory cleanup ═══"
  ensure_branch "fix/232-root-cleanup"

  mkdir -p archive/legacy

  # Move stale root files
  for f in DVWA_REPORT.md PROJECT_REVIEW_REPORT.md test_red_secops_agents.py; do
    [ -f "$f" ] && git mv "$f" archive/ && echo "  → $f archived"
  done

  # Move stale dirs to archive
  for d in candidates benchmarks examples templates tools workflow_results; do
    [ -d "$d" ] && git mv "$d" archive/ && echo "  → $d/ archived"
  done

  echo ""
  echo "Root items: $(ls -1 | wc -l)"
  commit_and_report 232 "chore(infra): audit and remove stale root-level artifacts (#232)"
}

# ─── #234 [HIGH] Harden .gitignore ────────────────────────
run_234() {
  echo "═══ #234: Harden .gitignore ═══"
  ensure_branch "fix/234-gitignore"

  cat >> .gitignore << 'GITIGNORE'

# === Added by #234 — harden gitignore ===

# Database files
*.sqlite
*.sqlite3
*.db

# Node
node_modules/
dist/

# Aider
.aider*
.aider.tags.cache.v3/

# Agent runtime state
agent_state/
workflow_checkpoints/

# Vector DB
qdrant/

# MkDocs
site/

# Python build
*.egg-info/
build/

# IDE
.idea/
.vscode/settings.json

# OS
Thumbs.db
.DS_Store

# Scratch scripts
scripts/gh-*.sh
scripts/do-*.sh
GITIGNORE

  git add .gitignore
  git commit -m "chore(infra): harden .gitignore — exclude build artifacts and runtime state (#234)

Closes #234
Co-Authored-By: Aider+Ollama <noreply@local>"
  echo "✓ Done."
}

# ─── #236 [HIGH] Scanner registry auto-discover ───────────
run_236() {
  echo "═══ #236: Scanner registry — auto-discover BaseScanner subclasses ═══"
  ensure_branch "feat/236-scanner-registry"

  aider \
    --message "Read .agents/tasks/issue-236.md for context.

Update packages/cherenkov/core/registry.py to auto-discover all BaseScanner subclasses:

1. Add a discover_scanners() function that:
   - Imports all modules in packages/cherenkov/scanners/
   - Finds all classes that inherit BaseScanner
   - Registers them automatically via registry.register()
   - Skips abstract classes and test classes
   
2. Use importlib and pkgutil to scan the scanners package
3. Add a module-level call: discover_scanners() at import time
4. Keep backward compatibility with manual registration
5. Add logging for each discovered scanner

Do NOT add any external dependencies. Keep it simple.
Follow the existing import pattern: from cherenkov.core.base_scanner import BaseScanner" \
    packages/cherenkov/core/registry.py \
    packages/cherenkov/core/base_scanner.py \
    packages/cherenkov/scanners/__init__.py

  commit_and_report 236 "feat(scanner): auto-discover BaseScanner subclasses in registry (#236)"
}

# ─── #237 [HIGH] Scan result aggregation pipeline ─────────
run_237() {
  echo "═══ #237: Scan result aggregation pipeline ═══"
  ensure_branch "feat/237-aggregator"

  aider \
    --message "Create packages/cherenkov/core/aggregator.py — a scan result aggregation pipeline.

Requirements:
1. class ScanAggregator with method aggregate(results: list[ScanResult]) -> ScanResult
2. Merge findings from N parallel scanner results into one unified ScanResult
3. Deduplicate findings by (target, scanner_name, finding title, location)
4. Sort findings by severity (CRITICAL first)
5. Sum duration_ms from all scanner results
6. Keep the highest severity finding when deduplicating

Also create tests/unit/test_aggregator.py with:
- test_aggregator_merges_results: 3 ScanResults with overlapping findings → deduplicated
- test_aggregator_empty: empty list → empty ScanResult
- test_aggregator_severity_sort: verify CRITICAL comes before LOW

Import: from cherenkov.core.base_scanner import ScanResult, Finding, Severity" \
    packages/cherenkov/core/base_scanner.py

  commit_and_report 237 "feat(core): scan result aggregation pipeline — merge findings from N scanners (#237)"
}

# ─── #238 [HIGH] Wire /api/v1/scan endpoint ───────────────
run_238() {
  echo "═══ #238: Wire POST /api/v1/scan with aggregator ═══"
  ensure_branch "feat/238-scan-endpoint"

  aider \
    --message "Wire the scan aggregation pipeline into the FastAPI /api/v1/scan endpoint.

In packages/cherenkov/api/main.py:
1. Import ScanAggregator from cherenkov.core.aggregator (if it exists, otherwise create inline)
2. Import the scanner registry from cherenkov.core.registry
3. In the POST /api/v1/scan handler:
   - Get all registered scanners from the registry
   - Run them concurrently with asyncio.gather (with timeout)
   - Aggregate results via ScanAggregator
   - Return the unified ScanResult as JSON
   - Broadcast scan progress via WebSocket

IMPORTANT: Do NOT break existing routes. Only modify the /api/v1/scan endpoint.
Follow MEISSNER invariant: scanners only reach the user-specified target URL." \
    packages/cherenkov/api/main.py \
    packages/cherenkov/core/registry.py

  commit_and_report 238 "feat(api): wire POST /api/v1/scan with aggregator pipeline (#238)"
}

# ─── #239 [HIGH] CI test matrix ───────────────────────────
run_239() {
  echo "═══ #239: Ensure test suite passes ═══"
  ensure_branch "test/239-ci-matrix"

  aider \
    --message "Fix any broken tests so the full test suite passes.

Run: pytest -m 'not (integration or ai_generated)' --tb=short -q

Look at test failures and fix them. Common issues:
- Import paths changed (src.cherenkov → cherenkov)
- Missing mock dependencies
- Stale test fixtures referencing deleted files

Do NOT delete tests. Fix imports and mocks instead.
If a test is genuinely obsolete, move it to tests/legacy/ instead of deleting." \
    tests/conftest.py

  commit_and_report 239 "test(ci): fix test suite — ensure 146+ tests pass (#239)"
}

# ═══════════════════════════════════════════════════════════
# SPRINT 3 — v1.5.0 Milestone (Phase 3: Scanner Graduation)
# ═══════════════════════════════════════════════════════════

# ─── #240 [HIGH] Graduate NetworkVulnerabilityScanner ──────
run_240() {
  echo "═══ #240: Graduate NetworkVulnerabilityScanner ═══"
  ensure_branch "feat/240-network-scanner"

  aider \
    --message "Graduate the NetworkVulnerabilityScanner to the BaseScanner contract.

Source: packages/cherenkov/autonomous_generated/scanners/networkvulnerabilityscanner.py
Destination: packages/cherenkov/scanners/network_vulnerability_scanner.py

1. Read the source file to understand what it detects
2. Create a new scanner at the destination that:
   - Inherits BaseScanner
   - Implements async scan(target, timeout) -> ScanResult
   - Uses self._http_request for all HTTP calls
   - Returns Finding objects with proper Severity levels
3. Register in packages/cherenkov/core/registry.py
4. Create tests/unit/test_network_vulnerability_scanner.py

Follow the pattern from existing graduated scanners like ssrf_scanner.py or xss_scanner.py." \
    packages/cherenkov/autonomous_generated/scanners/networkvulnerabilityscanner.py \
    packages/cherenkov/core/base_scanner.py \
    packages/cherenkov/scanners/ssrf_scanner.py \
    packages/cherenkov/core/registry.py

  commit_and_report 240 "feat(scanner): graduate NetworkVulnerabilityScanner to BaseScanner (#240)"
}

# ─── #241 [HIGH] Verify XXE scanner contract ──────────────
run_241() {
  echo "═══ #241: Verify XXE scanner BaseScanner contract ═══"
  ensure_branch "feat/241-xxe-verify"

  aider \
    --message "Verify and fix packages/cherenkov/scanners/xxe_scanner.py:

1. Confirm it inherits BaseScanner
2. Confirm it implements async scan(target, timeout) -> ScanResult
3. Confirm it uses self._http_request (not raw httpx/requests)
4. Confirm it returns proper Finding objects with Severity
5. Fix any issues found
6. Ensure it's registered in packages/cherenkov/core/registry.py
7. Verify tests/unit/test_xxe_scanner.py exists and covers the scanner" \
    packages/cherenkov/scanners/xxe_scanner.py \
    packages/cherenkov/core/base_scanner.py \
    packages/cherenkov/core/registry.py

  commit_and_report 241 "feat(scanner): verify XXE scanner BaseScanner contract (#241)"
}

# ─── #242 [MEDIUM] Graduate CVE Database Scanner ──────────
run_242() {
  echo "═══ #242: Graduate CVE Database Scanner ═══"
  ensure_branch "feat/242-cve-scanner"

  aider \
    --message "Graduate the CVE Database Scanner to BaseScanner.

Source: packages/cherenkov/autonomous_generated/scanners/cvedatabasescanner.py
Destination: packages/cherenkov/scanners/cve_database_scanner.py

Follow the same graduation pattern as other scanners. Inherit BaseScanner, implement async scan(), use self._http_request.
IMPORTANT: This scanner must NOT make external API calls to CVE databases (MEISSNER invariant). It should check for known CVE patterns in HTTP responses only." \
    packages/cherenkov/autonomous_generated/scanners/cvedatabasescanner.py \
    packages/cherenkov/core/base_scanner.py \
    packages/cherenkov/scanners/ssrf_scanner.py \
    packages/cherenkov/core/registry.py

  commit_and_report 242 "feat(scanner): graduate CVE Database Scanner to BaseScanner (#242)"
}

# ─── #245 [HIGH] Verify SSRF scanner contract ─────────────
run_245() {
  echo "═══ #245: Verify SSRF scanner BaseScanner contract ═══"
  ensure_branch "feat/245-ssrf-verify"

  aider \
    --message "Verify and fix packages/cherenkov/scanners/ssrf_scanner.py:

1. Confirm it inherits BaseScanner
2. Confirm async scan(target, timeout) -> ScanResult
3. Confirm self._http_request usage
4. Confirm proper Finding/Severity returns
5. Fix any issues
6. Verify registration in registry.py
7. Verify test coverage in tests/unit/" \
    packages/cherenkov/scanners/ssrf_scanner.py \
    packages/cherenkov/core/base_scanner.py \
    packages/cherenkov/core/registry.py

  commit_and_report 245 "feat(scanner): verify SSRF scanner BaseScanner contract (#245)"
}

# ═══════════════════════════════════════════════════════════
# DISPATCHER
# ═══════════════════════════════════════════════════════════
case "${1:-help}" in
  230) run_230 ;;
  232) run_232 ;;
  234) run_234 ;;
  236) run_236 ;;
  237) run_237 ;;
  238) run_238 ;;
  239) run_239 ;;
  240) run_240 ;;
  241) run_241 ;;
  242) run_242 ;;
  245) run_245 ;;

  sprint2)
    echo "══════ SPRINT 2 — v1.1.0 ══════"
    for t in 230 232 234 236 237 238 239; do
      echo "" && echo "━━━ Issue #$t ━━━"
      "run_$t" || echo "⚠ #$t had issues, continuing..."
      git checkout main 2>/dev/null || true
    done
    echo "══════ SPRINT 2 COMPLETE ══════"
    ;;

  sprint3)
    echo "══════ SPRINT 3 — v1.5.0 (Scanners) ══════"
    for t in 240 241 242 245; do
      echo "" && echo "━━━ Issue #$t ━━━"
      "run_$t" || echo "⚠ #$t had issues, continuing..."
      git checkout main 2>/dev/null || true
    done
    echo "══════ SPRINT 3 COMPLETE ══════"
    ;;

  all)
    echo "══════ ALL TASKS ══════"
    for t in 230 232 234 236 237 238 239 240 241 242 245; do
      echo "" && echo "━━━ Issue #$t ━━━"
      "run_$t" || echo "⚠ #$t had issues, continuing..."
      git checkout main 2>/dev/null || true
    done
    echo "══════ ALL COMPLETE ══════"
    ;;

  help|*)
    cat <<'EOF'

  ╔═══════════════════════════════════════════════════════════════╗
  ║  CHERENKOV — Aider Task Runner (GitHub-Aligned)              ║
  ╠═══════════════════════════════════════════════════════════════╣
  ║                                                              ║
  ║  🔴 SPRINT 2 — v1.1.0 (Phase 2)                              ║
  ║    230  MEISSNER: remove cloud configs     [git-only]        ║
  ║    232  Root cleanup                       [git-only]        ║
  ║    234  Harden .gitignore                  [git-only]        ║
  ║    236  Scanner registry auto-discover     [AI — backend]    ║
  ║    237  Scan result aggregator             [AI — backend]    ║
  ║    238  Wire POST /api/v1/scan             [AI — backend]    ║
  ║    239  CI test matrix fix                 [AI — tests]      ║
  ║                                                              ║
  ║  🟡 SPRINT 3 — v1.5.0 (Scanner Graduation)                   ║
  ║    240  Graduate NetworkVulnScanner        [AI — backend]    ║
  ║    241  Verify XXE scanner contract        [AI — backend]    ║
  ║    242  Graduate CVE Database Scanner      [AI — backend]    ║
  ║    245  Verify SSRF scanner contract       [AI — backend]    ║
  ║                                                              ║
  ║  Batch:                                                      ║
  ║    sprint2  — Run all Sprint 2 tasks sequentially            ║
  ║    sprint3  — Run all Sprint 3 tasks sequentially            ║
  ║    all      — Run everything                                 ║
  ║                                                              ║
  ║  Model: qwen2.5-coder:7b (Ollama) — $0                      ║
  ╚═══════════════════════════════════════════════════════════════╝

EOF
    ;;
esac
