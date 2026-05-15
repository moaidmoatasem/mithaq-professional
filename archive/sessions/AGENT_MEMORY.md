# Agent Session Memory

## Session 1 (2026-04-26, 4:11 PM EEST)

### Setup Complete ✅
- **Tools installed:** uv, Ollama (downloading models), Aider, pre-commit, pytest, ruff, bandit
- **AI Models:** llama3.2:3b-instruct-q4_K_M, qwen2.5-coder:7b-instruct-q4_K_M (downloading)
- **Repository:** Initialized at ~/cherenkov-dev
- **Agent rules:** Configured (.clinerules)
- **Pre-commit hooks:** Ready to install

### System Constraints
- **Hardware:** Ryzen 9 8945HS, 12GB WSL2 limit
- **Budget:** $0 (Gemini/Groq free tier only)
- **Timeline:** 30 weeks (Phase 0-5)
- **API Limits:** Gemini 15 RPM free, Groq 30 RPM free

### Architectural Decisions
1. **Model Selection:**
   - Code generation: qwen2.5-coder:7b (better than llama3.2:3b)
   - Code review: Groq Llama 3.3 70B (faster than Gemini)
   - Local execution: llama3.2:3b (lightweight)

2. **Development Workflow:**
   - TDD mandatory (tests before implementation)
   - Pre-commit blocks commits if coverage <80%
   - Git branch per feature (no direct commits to main)
   - Builder (Gemini) → Reviewer (Groq) → Human (merge)

3. **Security Standards:**
   - Skip NPU acceleration (use CPU only for stability)
   - All secrets in .env (never hardcoded)
   - Fail-closed error handling
   - Pydantic validation on all inputs

## Session 2: Apr 26-27, 2026 (Late Night Session)

**Branch:** feature/pydantic-gates
**Agent:** Human-driven with AI assistance planning

### Completed
- CloudInstruction Pydantic schema
- 6 comprehensive unit tests
- Security validators: AWS keys, JWT tokens, prompt injection
- Type safety: Literal actions, confidence bounds
- Hallucination prevention: ConfigDict(extra='forbid')

## Session 3 (Previous)
- AblationSanitizer with HMAC signature generation and verification

## Session 4 (2026-05-10) — Package Restructure & Clean Architecture

**Branches:** Multiple feature branches covering Phases 1-5

### Summary
Complete transformation of CHERENKOV from flat `src/cherenkov/` to clean 5-pillar architecture.

### What Was Done

#### Phase 1: Cleanup
- Removed stale backup directories, consolidated Dockerfiles (4→1 in deploy/), compose files (3→1)
- Updated .github/CODEOWNERS and release-drafter.yml

#### Phase 2: Package Restructure
- Created `packages/cherenkov/` as new source root
- Moved all `src/cherenkov/` code → `packages/cherenkov/`
- Merged flat config/schemas/ablation/ai/storage into `core/` subdirectories
- Reorganized root-level flat files into `cli/` and `orchestration/` subpackages with re-exporting `__init__.py` files
- Created stubs and fixed 18+ imports

#### Phase 3: Test Restructure
- Created `tests/packages/` mirroring source layout
- Moved 22 test files
- Marked 11 env-dependent tests with `@pytest.mark.integration`

#### Phase 4: Design System
- Unified design tokens in `cherenkov-portal/design-tokens/tokens.json`
- Reorganized React portal to Atomic Design (atoms/molecules/organisms/templates/pages)

#### Phase 5: Clean Code
- **Error Hierarchy:** 15 typed exception types in `core/exceptions.py`
- **Logging:** Replaced all `print()` in 3 core modules with logging
- **God-class splitting:** Extracted `WorkflowExecutor`, `AgentRegistry`, `WorkflowScheduler` from `orchestration_api.py`
- **Type annotations:** Added to `orchestration_api.py`, `scan_runner.py`, plus 8 more modules
- **Event bus injection:** Constructor injection pattern in `scan_runner.py`
- **Stale cleanup:** Removed `src/cherenkov/` directory and old `.pth` editable install

### Key Decisions
- **Single package:** Logical subpackages under `packages/cherenkov/`, not separate installable packages
- **Core consolidation:** All infrastructure under `core/` (config, schemas, ablation, AI, storage, events, exceptions)
- **Test mirroring:** tests mirror source under `tests/packages/`
- **AI-generated code:** Preserved in-tree with `GENERATED.md` markers, excluded from coverage
- **Logging over print:** `logging.getLogger(__name__)` in all hand-written code
- **Constructor injection:** EventBus passed explicitly rather than module-level singletons

### Current Architecture
```
packages/cherenkov/
├── core/          — events, exceptions, registry, base_scanner, engine, ablation, storage, schemas, config
├── scanners/      — scan_runner, header_scanner, unified_scanner, http_methods, tls_detection
├── orchestration/ — agent_registry, workflow_scheduler, orchestration_api, types, result_persistence, agent_factory
├── agents/        — architect, developer, tester, tokamak, cloud providers, micro_swarm stubs
├── crews/         — autonomous dev teams, security crew
├── api/           — FastAPI server
├── cli/           — Typer CLI
├── dev_crew/      — swarm orchestrator, scanner generator
├── autonomous_generated/ — AI-generated code (excluded)
├── micro_swarm/   — stubs (3 files)
```

### Test Status
- 25 orchestration tests pass (including 17 new: 10 AgentRegistry + 7 WorkflowScheduler)
- 26 core/scanner/storage/ablation/events tests pass
- 1 pre-existing crewai dependency failure
- 22 env-dependent/integration/AI-generated tests as expected

### Files Modified This Session
- `packages/cherenkov/scanners/scan_runner.py` — event_bus injection
- `packages/cherenkov/core/__init__.py` — EventBus export
- `packages/cherenkov/core/events.py` — (unchanged, backward compat preserved)
- `packages/cherenkov/orchestration/orchestration_api.py` — god-class delegation
- `packages/cherenkov/orchestration/agent_registry.py` — NEW (AgentRegistry class)
- `packages/cherenkov/orchestration/workflow_scheduler.py` — NEW (WorkflowScheduler class)
- `packages/cherenkov/orchestration/types.py` — NEW (AgentID, WorkflowResult dataclasses)
- `packages/cherenkov/orchestration/__init__.py` — updated exports
- `tests/packages/orchestration/test_agent_registry.py` — NEW (10 tests)
- `tests/packages/orchestration/test_workflow_scheduler.py` — NEW (7 tests)
- `tests/packages/orchestration/test_orchestration_api.py` — fixed patch targets
- `tests/packages/core/test_overseer.py` — fixed CognitiveLoopException→CognitiveLoopError
- `tests/packages/autonomous_generated/test_smartretrier_httpx.py` — fixed import path
- `tests/verify_fix.py` — fixed import paths (src.cherenkov→cherenkov)
- `benchmarks/benchmark_smartretrier.py` — fixed import path
- 8 modules annotated with types (header_scanner, unified_scanner, tokamak, sanitized_output, autonomous_developer_crew, autonomous_dev_team, api/main, cli/main)
- STATUS.md, TODO.md, AGENT_MEMORY.md — updated

### Blockers
- crewai/pydantic compatibility issue (pre-existing, doesn't block development)
