# Task: Issue #232 — Audit and remove stale root-level artifacts

**Branch:** `fix/232-root-cleanup`
**Labels:** `priority:medium, chore, phase-2, status:in-progress`
**Milestone:** v1.1.0
**PR must contain:** `Closes #232`

## Context

The repo root has accumulated stale directories and files from earlier development.
The root should be clean: only `packages/`, `tests/`, `docs/`, `.github/`, `deploy/`,
`.agents/`, `scripts/`, `archive/`, and standard config files (pyproject.toml, Dockerfile, etc.).

## Items to audit

| Item | Action |
|---|---|
| `DVWA_REPORT.md` | Move to `archive/` or `docs/reports/` |
| `PROJECT_REVIEW_REPORT.md` | Move to `archive/` or `docs/reports/` |
| `workflow_results/` | Move to `archive/workflow_results/` |
| `candidates/` | Move to `archive/candidates/` |
| `benchmarks/` | Move to `archive/benchmarks/` — or `tests/benchmarks/` if active |
| `examples/` | Move to `docs/examples/` or `archive/examples/` |
| `templates/` | Move to `archive/templates/` or `packages/cherenkov/templates/` if active |
| `tools/` | Move to `scripts/tools/` or `archive/tools/` |
| `proxy_server.py` | Move to `scripts/` or `archive/` |
| `test_api.sh` | Move to `tests/` or `scripts/` |
| `test_red_secops_agents.py` | Move to `tests/` |
| `agent_state/` | Add to `.gitignore`, move to `archive/` if committed |
| `logs/` | Add to `.gitignore`, remove from tracking |
| `data/` | Audit contents — move or gitignore |
| `manifests/` | Keep if k8s manifests, else archive |
| `.aider*` files | Add to `.gitignore` |

## What to do

1. **Create archive subdirectories** as needed:
   ```bash
   mkdir -p archive/reports archive/legacy
   ```

2. **Move stale files**:
   ```bash
   git mv DVWA_REPORT.md archive/reports/
   git mv PROJECT_REVIEW_REPORT.md archive/reports/
   git mv workflow_results/ archive/
   git mv candidates/ archive/
   git mv benchmarks/ archive/
   git mv examples/ archive/
   git mv templates/ archive/
   git mv tools/ archive/
   git mv proxy_server.py archive/legacy/
   git mv test_api.sh tests/
   git mv test_red_secops_agents.py tests/
   ```

3. **Audit remaining items** (data/, manifests/, logs/) — decide per-item

4. **Update .gitignore** for items that should never be committed (logs/, agent_state/, .aider*)

## Files to modify

- Root directory — many files moved
- `.gitignore` — add patterns for transient files
- `archive/` — receives moved files

## Verify

```bash
# Root should be clean — only expected dirs and config files
ls -la | grep -v '^\.' | grep -v packages | grep -v tests | grep -v docs | grep -v deploy | grep -v archive | grep -v scripts | grep -v .github | grep -v .agents

# Lint
ruff format packages/ && ruff check packages/ --ignore W,S,B

# Tests still pass
pytest -m "not (integration or ai_generated)" --tb=short
```
