#!/bin/bash
set -e

gh issue create \
  --title "[TASK] Audit and migrate legacy compliance/ modules" \
  --label "task,priority:high,area:api" \
  --body "$(cat <<'EOF'
## Description
packages/cherenkov/compliance/ already contains mapper.py, process_mapper.py, reports.py. Audit these and either delete (if unused) or migrate logic into the plugin shape before the plugin system lands.

## Acceptance Criteria
- [ ] grep -r "from cherenkov.compliance" packages/ tests/ mapped
- [ ] Each file: kept / migrated / deleted with justification
- [ ] pytest -q green
- [ ] PR <=8 files, <=400 lines

## Priority
priority:high
## Area
area:api
## Agent Autonomy
Human review required
## Milestone
v0.2.0-beta
## Assigned Agent
Jules
EOF
)"

gh issue create \
  --title "[TASK] Build regulatory-agnostic compliance plugin system" \
  --label "task,priority:critical,area:api" \
  --body "$(cat <<'EOF'
## Description
Plugin architecture for compliance frameworks. Adding a framework = drop one .py in packages/cherenkov/compliance/. Depends on legacy cleanup issue.

## Scope
- compliance/base.py, registry.py, egyfincsf.py, samacsf.py, owasptop10.py
- api/main.py: GET /api/v1/compliance/frameworks, /api/v1/scan/{id}/compliance/{fw}
- tests/packages/compliance/test_registry.py

## Acceptance Criteria
- [ ] 3 frameworks discovered automatically
- [ ] CWE-89 maps to PR-04 / 4.4 / A03
- [ ] Unknown framework returns 400
- [ ] mypy clean
- [ ] PR <=8 files, <=400 lines

## Priority
priority:critical
## Area
area:api
## Agent Autonomy
Human review required
## Milestone
v0.2.0-beta
## Assigned Agent
Jules
## Branch
feat/compliance-plugin-system
EOF
)"

gh issue create \
  --title "[TASK] Device-aware LLM model selector" \
  --label "task,priority:high,area:agent" \
  --body "$(cat <<'EOF'
## Description
Detect hardware, recommend Ollama models per role, generate LiteLLM config, expose via API.

## Scope
- ai/model_selector.py
- api/main.py: /api/v1/models/{recommend,litellm-config,available}
- scripts/setup_models.sh
- pyproject.toml: add psutil
- tests/packages/ai/test_model_selector.py

## Acceptance Criteria
- [ ] Tier classification (low/medium/high) works
- [ ] Foundation-Sec-8B chosen for architect when VRAM>=5.5GB
- [ ] No model exceeds 80% effective memory
- [ ] Groq fallback in generated config
- [ ] PR <=8 files, <=400 lines

## Priority
priority:high
## Area
area:agent
## Agent Autonomy
Human review required
## Milestone
v0.2.0-beta
## Assigned Agent
Jules
## Branch
feat/model-selector
EOF
)"

gh issue create \
  --title "[TASK] Fix and stabilize HUD dashboard" \
  --label "task,priority:high,area:ui" \
  --body "$(cat <<'EOF'
## Description
Dashboard pass: central auth headers, framework dropdown, compliance auto-render, ModelStatus widget (read-only), strip DAQIQ, v0.2.0-beta. Depends on compliance + model-selector issues merged.

## Scope (web/ ONLY)
- src/lib/api.ts central getAuthHeaders
- src/components/ScanForm.tsx framework dropdown
- src/components/ComplianceReport.tsx (new)
- src/components/ModelStatus.tsx (new, read-only)
- src/components/FindingsTable.tsx new columns
- Global: DAQIQ->CHERENKOV, 132+->5+, version v0.2.0-beta

## Acceptance Criteria
- [ ] No 401/404 in console
- [ ] Scan with framework renders compliance report
- [ ] ModelStatus shows tier + active models
- [ ] No DAQIQ string remains
- [ ] npm run build clean, dist copied to api/static/
- [ ] PR <=8 files, <=400 lines

## Priority
priority:high
## Area
area:ui
## Agent Autonomy
Human review required
## Milestone
v0.2.0-beta
## Assigned Agent
Antigravity
## Branch
feat/dashboard-fix-consistency
EOF
)"

gh issue create \
  --title "[TASK] Definitive start_cherenkov.sh orchestrator" \
  --label "task,priority:medium,area:infra" \
  --body "$(cat <<'EOF'
## Description
One-command boot: Qdrant, DVWA, Ollama, LiteLLM, API. Health-checks + JWT smoke test. Depends on model-selector (produces litellm-config.yaml).

## Scope
- scripts/start_cherenkov.sh
- README.md quick-start pointer

## Acceptance Criteria
- [ ] Idempotent alias registration
- [ ] Kills stale uvicorn/litellm
- [ ] 5 services health-checked with marks
- [ ] JWT smoke test passes
- [ ] shellcheck clean
- [ ] PR <=2 files, <=200 lines

## Priority
priority:medium
## Area
area:infra
## Agent Autonomy
Human review required
## Milestone
v0.2.0-beta
## Assigned Agent
Jules
## Branch
feat/startup-script
EOF
)"

gh issue create \
  --title "[TASK] E2E demo: scan -> compliance -> signed PDF" \
  --label "task,priority:critical,area:api" \
  --body "$(cat <<'EOF'
## Description
Exit criterion for v0.2.0-beta. Run DVWA scan with EGY-FIN CSF, render compliance report, emit ONE signed PDF (SHA-256 + RFC 3161). Depends on all four prior issues.

## Scope
- compliance/pdf_renderer.py
- api/main.py: GET /api/v1/scan/{id}/compliance/{fw}/pdf
- tests/integration/test_e2e_demo.py

## Acceptance Criteria
- [ ] PDF generated from real DVWA scan
- [ ] Embedded SHA-256 + freetsa.org timestamp
- [ ] Verification command validates signature
- [ ] Artifact attached to issue
- [ ] PR <=6 files, <=400 lines

## Priority
priority:critical
## Area
area:api
## Agent Autonomy
Human review required
## Milestone
v0.2.0-beta
## Assigned Agent
Jules
## Branch
feat/e2e-demo-artifact
EOF
)"
