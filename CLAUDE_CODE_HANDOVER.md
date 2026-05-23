# CHERENKOV — Claude Code Handover
# Paste this entire file at the start of every Claude Code session

---

## PROJECT

CHERENKOV: Sovereign AI security platform.
Air-gapped. Cryptographic proof chain. CBE/EGY-FIN CSF compliance.
Zero cloud egress. Local-first. MIT Licensed.

Repo: git@github.com:moaidmoatasem/cherenkov-professional.git
Machine: WSL2 Ubuntu 24.04 / Ryzen 7 / 16GB / RTX 5060 8GB

---

## START EVERY SESSION WITH

```bash
cd ~/cherenkov-professional
source venv/bin/activate
export CHERENKOV_JWT_SECRET=cherenkov-sovereign-audit-key-2024
export PYTHONPATH=$PYTHONPATH:$(pwd)/packages
python scripts/sync_context.py 2>/dev/null; cat .cherenkov_context 2>/dev/null || git log --oneline -5
```

---

## NON-NEGOTIABLE INVARIANTS

1. Package path: packages/cherenkov/ — NEVER src/
2. Imports: from cherenkov.X import Y
3. Never commit to main — branch → PR → Moaid merges
4. Zero cloud egress — MEISSNER enforces this
5. ABLATION sanitizes before any external LLM call
6. TOKAMAK required for HIGH/CRITICAL findings
7. freetsa.org for RFC 3161 timestamps — never AWS/GCP
8. venv must be active before any Python command
9. Pre-commit: ruff format + bandit -ll before every commit

---

## CANONICAL NAMES

CHERENKOV / TENSOR / KINETIC / AEGIS / LATTICE / TOKAMAK
MEISSNER / ABLATION / CherenkovTrace

NEVER: DAQIQ, MITHAQ, src.cherenkov, Al-Muhandis, Al-Burhan

---

## CURRENT STATE (May 2026)

WORKING:
- FastAPI + JWT auth (POST /api/v1/auth/token → real JWT)
- WebSocket /ws/live → health_pulse every 5s
- LATTICE bridge (embed_and_store, query_similar, label_fp)
- 5 validated scanners in packages/cherenkov/scanners/
- React dashboard at packages/cherenkov/api/static/
- Test coverage 47%, 199 passing
- ABLATION schemas, JWT middleware, dev_crew/ agents

BROKEN — FIX IN ORDER:
P0: Scan returns 401 (JWT not sent from FE)
    File: packages/cherenkov/web/src/lib/api.ts
    Fix: add Authorization header to scan POST request

P0: API requires manual env var export each session
    Fix: ensure .env loaded via python-dotenv in main.py

P1: Repo description "132+ scanners" (GitHub UI)
P1: Release "DAQIQ v0.1.0-alpha" (GitHub UI)
P1: mcp_config.json committed (git rm it)
P1: Root still has dev artifacts

P2: TOKAMAK never executes real PoC
P2: EGY-FIN CSF mapping missing
P2: RFC 3161 timestamp not wired

---

## KEY FILES

```
packages/cherenkov/api/main.py              FastAPI app
packages/cherenkov/api/middleware/auth.py   JWT auth
packages/cherenkov/api/routers/             API routers
packages/cherenkov/api/static/              Built React dashboard
packages/cherenkov/core/base_scanner.py     BaseScanner ABC
packages/cherenkov/core/engine.py           ScanEngine
packages/cherenkov/core/tokamak.py          PoC sandbox (partial)
packages/cherenkov/core/storage/database.py SQLite WAL
packages/cherenkov/core/ablation/           ABLATION schemas
packages/cherenkov/scanners/                5 validated scanners
packages/cherenkov/ai/lattice_bridge.py     LATTICE (Qdrant)
packages/cherenkov/ai/model_router.py       TENSOR/KINETIC routing
packages/cherenkov/agents/                  AI agents
packages/cherenkov/compliance/              EGY-FIN CSF (planned)
packages/cherenkov/web/                     React source (Antigravity domain)
deploy/docker-compose.yml                   Canonical compose
.env                                        Secrets
venv/                                       Python venv
```

---

## SERVICES

API:      http://localhost:8000
Dashboard: http://localhost:8000/static/index.html  admin/admin
LATTICE:  http://localhost:6333
DVWA:     http://localhost:80  admin/password
Ollama:   http://localhost:11434  llama3.2:3b + qwen2.5-coder:7b

---

## ARCHITECTURE

```
C2 DASHBOARD (React/TypeScript)
    ↕ REST + WebSocket
FASTAPI HUB (port 8000)
    ├── Auth (JWT)
    ├── /ws/live (WebSocket)
    ├── /api/v1/scan
    └── /api/v1/architect (PLANNED)
         ↓
SECURITY ARCHITECT LAYER (PLANNED)
    deepseek-r1:8b → EngagementPlan
         ↓              ↓
  RED TEAM          SECOPS
  (PLANNED)         (PLANNED)
         ↓
CHERENKOV CORE
    MEISSNER → zero egress
    ABLATION → PII strip
    TOKAMAK  → PoC execution
    LATTICE  → Qdrant memory
    TENSOR   → cloud LLM (sanitized)
    KINETIC  → local Ollama
    CherenkovTrace → SHA-256 + RFC 3161
```

---

## TOOL ROLES (Do Not Overlap)

Claude Code:   Architecture, multi-file refactors, system design
Jules:         Agent tasks, API fixes, scanner validation
Aider:         Git-native pair programming (local terminal)
Cline:         Autonomous file edits in IDE
Continue.dev:  Inline autocomplete
Antigravity:   packages/cherenkov/web/ ONLY
Kilo:          Quick terminal tasks

---

## BRANCH + COMMIT FORMAT

Branch: feat/N-description or fix/N-description
Commit: type(scope): description (#N)
        Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

Pre-commit:
  ruff format packages/
  ruff check packages/ --ignore W
  bandit -r packages/ -ll
  pytest -m "not integration" --tb=short -q

---

## HANDOVER FORMAT

When finishing a session, output:

## Session Summary
Branch: [name]
PRs opened: [numbers]
Files changed: [list]
Tests: [X passing, Y failing]
Next task: [single specific task]
Blockers: [if any]

---

## IMMEDIATE TASK FOR THIS SESSION

Fix scan 401 — this is the only P0 blocker.

Read these two files:
1. packages/cherenkov/web/src/lib/api.ts
   Find the scan() or submitScan() function
   Add Authorization: Bearer header from sessionStorage

2. packages/cherenkov/api/main.py around line 494
   Verify the scan endpoint uses Depends(get_current_user)

Test:
  TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/token \
    -H 'Content-Type: application/json' \
    -d '{"username":"admin","password":"admin"}' \
    | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

  curl -s -X POST http://localhost:8000/api/v1/scan \
    -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/json' \
    -d '{"target_url":"http://localhost:80"}'

Must return 200 with findings. Not 401.

After fix: rebuild FE if api.ts changed
  cd packages/cherenkov/web && npm run build
  cp -r dist/* ../api/static/

Commit on branch: fix/scan-401-auth
Open PR.
