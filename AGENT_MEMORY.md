# Agent Session Memory

> Canonical location: repo root (`AGENT_MEMORY.md`)
> Previous versions archived in `archive/sessions/AGENT_MEMORY.md`

---

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

---

## Session 2: Apr 26-27, 2026 (Late Night Session)

**Branch:** feature/pydantic-gates
**Agent:** Human-driven with AI assistance planning

### Completed
- CloudInstruction Pydantic schema
- 6 comprehensive unit tests
- Security validators: AWS keys, JWT tokens, prompt injection
- Type safety: Literal actions, confidence bounds
- Hallucination prevention: ConfigDict(extra='forbid')

---

## Session 3 (Previous)

- AblationSanitizer with HMAC signature generation and verification

---

## Session 4 (2026-05-10) — Package Restructure & Clean Architecture

**Branches:** Multiple feature branches covering Phases 1-5

### Summary
Complete transformation of CHERENKOV from flat `src/cherenkov/` to clean 5-pillar architecture.

### What Was Done
- **Phase 1:** Cleanup — removed stale backups, consolidated Dockerfiles (4→1), compose files (3→1)
- **Phase 2:** Package restructure — `packages/cherenkov/` as new source root
- **Phase 3:** Test restructure — `tests/packages/` mirroring source layout
- **Phase 4:** Design System — unified tokens, Atomic Design
- **Phase 5:** Clean Code — error hierarchy, logging, god-class splitting, type annotations

### Key Decisions
- **Single package:** Logical subpackages under `packages/cherenkov/`, not separate installable packages
- **Core consolidation:** All infrastructure under `core/` (config, schemas, ablation, AI, storage, events, exceptions)
- **Test mirroring:** tests mirror source under `tests/packages/`
- **AI-generated code:** Preserved in-tree with `GENERATED.md` markers, excluded from coverage
- **Logging over print:** `logging.getLogger(__name__)` in all hand-written code
- **Constructor injection:** EventBus passed explicitly rather than module-level singletons

### Test Status
- 25 orchestration tests pass (including 17 new: 10 AgentRegistry + 7 WorkflowScheduler)
- 26 core/scanner/storage/ablation/events tests pass
- 1 pre-existing crewai dependency failure
- 22 env-dependent/integration/AI-generated tests as expected

### Blockers
- crewai/pydantic compatibility issue (pre-existing, doesn't block development)

---

## Session 5 (2026-05-22 → 2026-05-24) — Agentic Handover & C2 Hub

**Agents involved:** Claude Code (coordinating), Antigravity (frontend/documentation)
**Branches:** `feat/web-c2-handover-docs`, various PRs (#298, #300, #351)

### Summary
Established the Agentic Handover Protocol, resolved multi-agent coordination issues, and began the handover from Claude Code to a new agent-agnostic C2 Hub (Control Tower).

### What Was Done

#### Agentic Handover Protocol
- Created `docs/development/agentic-handover-protocol.md` — formal 3-tier alert system (Green/Yellow/Red), Handover Packet template, `AgentStateStore` serialization API, Code of Conduct
- Opened PR #300 for the protocol document

#### AgentStateStore
- Created `agent_state/` directory with serialized JSON states:
  - `antigravity.json` — frontend agent (idle, 183/183 tests passed)
  - `source-1.json` — developer role (idle)
  - `target-1.json` — tester role (idle)
- `snapshots/` directory created but empty (handoff snapshots not yet generated)

#### PR #298 Conflict Resolution
- Resolved merge conflicts in local repository for PR #298

#### Issue Progression
- #230 (MEISSNER cloud configs removal) — MERGED
- #232 (Root cleanup) — MERGED
- #236 (Scanner registry) — PR in progress, has merge conflict in `database.py`
- #237 (Aggregation pipeline) — PR in progress

#### C2 Hub Concept
- Identified need for agent-agnostic "Control Tower" that any agent (Claude, Antigravity, Jules) can assume
- Performed comprehensive repo audit — found all handover artifacts
- Identified 7 gaps in handover readiness (see `STATUS.md`)
- Created root-level `STATUS.md`, `TODO.md`, `AGENT_MEMORY.md` to close gaps

### Key Decisions
- **State files at root:** `STATUS.md`, `TODO.md`, `AGENT_MEMORY.md` belong at repo root, not buried in `archive/sessions/`
- **`.agents/context.md` is SSOT:** The freshest coordination file; all agents should read it first
- **Agent-agnostic coordination:** The C2 Hub role can be assumed by any agent, not just Claude Code
- **Handover Packet required:** Per the protocol, outgoing agents MUST produce a formal packet before handing off

### Architectural Decisions
1. **Agent State Persistence:** JSON files in `agent_state/` following the `AgentState` schema
2. **Handoff Snapshots:** Target directory `agent_state/snapshots/` — to be populated by `create_handoff_snapshot()`
3. **Three-tier Alert System:** Green (<75% context), Yellow (75-90%), Red (>90%) — triggers state persistence automatically
4. **Domain Boundaries Enforced:**
   - Antigravity → `packages/cherenkov/web/src/` only
   - Jules → `packages/cherenkov/api/`, `packages/cherenkov/core/` only
   - Claude Code / C2 Hub → cross-functional coordination

### Current Test Count
- **183 tests passing** (up from 51 in Session 4)

### Active Blockers
- PR #351 has merge conflict in `packages/cherenkov/core/storage/database.py`
- `agent_state/snapshots/` is empty — no programmatic handoff snapshot exists yet
