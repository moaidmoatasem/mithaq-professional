# Task: Issue #223 — Root directory cleanup

**Branch:** `fix/223-root-cleanup`
**Labels:** `priority:critical, area:infra, chore`
**PR must contain:** `Closes #223`

## Why this is P0

50+ development artifacts at repo root create a catastrophic first impression.
Every AI agent session starts by scanning root — they read stale context.
The old Flask file `cherenkov_web.py` implies Flask is still in use.

## What to do

### 1. Move dev scripts to `scripts/`

These should be moved (not deleted — they may have value):

```
batch_scan.sh               → scripts/
demo_complete_system.sh     → scripts/
get-docker.sh               → scripts/
monitor_perfection.sh       → scripts/
phase1_open_source.sh       → scripts/
run_all_systems.sh          → scripts/
run_all_systems.ps1         → scripts/
run_autonomous_agent.sh     → scripts/
setup.sh                    → scripts/
scan_report_20260516_*.json → scripts/output/ (or delete — stale test output)
```

### 2. Move legacy code to `archive/`

```
cherenkov_web.py            → archive/  (old Flask entry point, replaced by FastAPI)
cherenkov_simple_scanner.py → archive/
cherenkov_cli.py            → archive/  (superseded by packages/cherenkov/cli/)
session_manager.py          → archive/
system_dashboard.py         → archive/
```

### 3. Move root test files to `tests/`

```
test_batched_parallel.py    → tests/legacy/
test_complete_system.py     → tests/legacy/
test_full_autonomous_crew.py→ tests/legacy/
test_full_dev_team.py       → tests/legacy/
test_gemini_planner.py      → tests/legacy/
test_groq_planner.py        → tests/legacy/
test_hybrid_orchestrator.py → tests/legacy/
test_local_agent.py         → tests/legacy/
test_parallel_agents.py     → tests/legacy/
test_production_ready.py    → tests/legacy/
test_redactor.py            → tests/legacy/
test_rename.py              → tests/legacy/
```

Note: Add `tests/legacy/` to pytest ignore list in `pyproject.toml` (these are legacy, not the canonical suite).

### 4. Move output artifacts

```
pytest_output.txt           → delete (stale)
validation_results.json     → delete or archive/
workflow_results/           → archive/ or delete
scan_report_*.json          → delete (stale test output)
```

### 5. Clean up extra configs

```
wrangler.jsonc, wrangler.toml  → only if Cloudflare Workers is unused; move to archive/ or delete
package.json (root)            → check if needed; if not, delete (web package.json is in packages/cherenkov/web/)
nginx.conf (root)              → move to deploy/ if used; otherwise delete
```

### 6. Root after cleanup should contain ONLY

```
packages/         tests/           docs/            .github/
deploy/           .agents/         .continue/       scripts/
archive/          pyproject.toml   README.md        ARCHITECTURE.md
CLAUDE.md         AGENTS.md        GEMINI.md        CHANGELOG.md
LICENSE           SECURITY.md      CONTRIBUTING.md  docker-compose.yml
opencode.jsonc    mkdocs.yml       mcp_config.json  assets/
```

## Verify

```bash
# Root should have < 25 items after cleanup
ls -1 | wc -l

# Canonical test suite still passes
pytest -m "not (integration or ai_generated)" --tb=short
```
