# CHERENKOV Agent Memory
## Technical Decisions & Lessons Learned

### Architecture
- **Monorepo layout**: All source under `packages/cherenkov/`. Root-level `.py` scripts are legacy — do not import from them.
- **Import path**: Always `from cherenkov.core.X import Y`, never `from src.cherenkov.X`.
- **`@` alias** in React maps to `packages/cherenkov/web/` (package root), so imports are `@/src/lib/api`, `@/src/hooks/useMetrics`, etc.

### Backend (FastAPI — `packages/cherenkov/api/main.py`)
- `/api/v1/*` routes are on the `v1 = APIRouter(prefix="/api/v1")` registered at the bottom.
- WebSocket is at `/ws/live` — singleton broadcast hub `_ws_clients: Set[WebSocket]`.
- Scan history is an in-memory list `_scan_history` (last 50) — **not yet persisted to SQLite**. This is Sprint 3/4 work.
- Health endpoint returns static `nodes` dict — not yet wired to real Ollama/process checks.
- CORS: `allow_origins` from env `cherenkov_CORS_ORIGINS`, default includes `:3000` and `:8000`.

### Frontend (React — `packages/cherenkov/web/`)
- `src/lib/api.ts` is the single source of truth: `API_BASE`, `getWsUrl()`, typed interfaces, fetch helpers.
- Vite proxy in dev: `/api → http://127.0.0.1:8000`, `/ws → ws://127.0.0.1:8000`.
- `useLiveEvents.ts` — singleton WebSocket, 3s reconnect, module-level state (one WS per page load).
- Scan results flow: `TacticalOperationsPanel` → `submitScan()` → `cherenkov:scan_complete` CustomEvent → `ThreatIntelPanel`.
- `DISABLE_HMR=true` env var disables hot reload (used by Antigravity preview).

### Testing
- **Virtual Environments**: Use `.venv/Scripts/pytest.exe` (Windows) or `.venv/bin/pytest` (Linux/CI).
- **Integration tests** are gated by marker `integration` + `ai_generated` — correctly skipped when real API keys absent.
- **CI runs**: `pytest -m "not (integration or ai_generated)"` → 68 pass, 7 skip.
- Test files live in `tests/` (not `packages/`).

### Encoding / Windows
- Python CLI scripts: avoid Unicode chars (`──`) in print output — Windows CMD (cp1252) throws `UnicodeEncodeError`. Use ASCII equivalents.
- Git bash on Windows: use `git -C /path/to/repo` for absolute paths when CWD changes across tool calls.

### Agent Coordination
- **Antigravity (Google IDE)**: Runs Vite dev server on `:3000`. "Reactive state is disabled" = Google server-side flag, resolves itself — not locally fixable. Extension host crash was caused by `ms-python.vscode-python-envs` + `meta.pyrefly` — both renamed to `.disabled` in `C:/Users/moaid/.antigravity/extensions/`.
- **Claude GitHub Actions**: Triggered by `@claude` in issue/PR comments. Workflow: `.github/workflows/claude.yml`. Needs `ANTHROPIC_API_KEY` secret.
- **Continue.dev**: Local Qwen 3.5 via Ollama. Config: `.continue/agents/new-config.yaml`. MCP servers not yet wired.
- **Autonomous pipeline**: `.github/workflows/autonomous-dev.yml` — daily at 2AM UTC, runs `scripts/autonomous_roadmap_executor.py --batch-size 3`, PRs into `auto-dev/<run_number>`.

### Sprint Boundaries
- Sprint 1 (BaseScanner) ✅ — `packages/cherenkov/core/base_scanner.py`
- Sprint 2 (Parallel + AIMD) ✅ — `circuit_breaker.py`, `ai_workflows_orchestrator.py`
- Sprint 3 (TOKAMAK Docker) 🔄 — `core/tokamak.py` (223 lines) exists, Docker wire-up + Command pattern pending
- Sprint 4 (HITL) ⏳ — not started
- Sprint 5 (Compliance) ⏳ — not started

### Known Issues / Gotchas
- `_scan_history` list is lost on server restart — must be moved to SQLite WAL (Sprint 4).
- `autonomous_generated/` contains many broken/duplicate files from early swarm generation — do not refactor without reading first.
- `src/cherenkov/` (old path) may still exist in some legacy scripts — do not use; canonical path is `packages/cherenkov/`.
- `pytest_output.txt` and `scan_report_*.json` are gitignored runtime files — do not commit.
