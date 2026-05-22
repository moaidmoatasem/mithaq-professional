# 🧠 CHERENKOV — Agentic Thought Tracing & Debugging Logs

This log serves as a chronological record of the cognitive reasoning, design trade-offs, and thoughts of Cherenkov agents before executing code changes.

---

## 📋 1. Agentic Thought Tracing Protocol

To ensure full transparency and permit human oversight, every agent working in this repository must record their thoughts prior to executing significant changes, following this schema:

```markdown
### 🕒 [YYYY-MM-DD HH:MM] — [Agent Persona (e.g. Antigravity)]
- **Context & Goal**: What issue or request is being addressed?
- **Trade-Offs & Architectural Considerations**:
  - *Option A (Pros/Cons)* vs *Option B (Pros/Cons)*
- **Proposed Logic Flow**: Step-by-step logic breakdown.
- **Verification Vector**: How will correctness be proven?
```

---

## 📝 2. Chronological Thought Log Entries

### 🕒 2026-05-22 17:55 — Antigravity (Google IDE Frontend Agent)

- **Context & Goal**: Establish an Agentic console and consolidation SSOT for the entire workspace. Integrate progress from historical access verification, API technical debt addressing, and WS proxy tunnel authorization fixes.
- **Trade-Offs & Architectural Considerations**:
  - *Option A (Directly edit core Python and React files)*: Risk of breaking downstream features and breaching Antigravity's strict frontend-only domain boundaries.
  - *Option B (Introduce a workspace-wide `docs/agentic_console/` bridging layer)*: Clean, safe, zero-impact on production execution, yet acts as a central repository for cross-agent coordination and human inspection. Highly structured.
  - *Decision*: **Option B chosen**. This perfectly answers the user's need for consolidation and SSOT without risking workspace health.
- **Proposed Logic Flow**:
  1. Create a structured directory `/home/moaid/cherenkov-professional/docs/agentic_console/`.
  2. Implement `MASTER_CONSOLE.md` consolidating the milestones and previous session outcomes.
  3. Implement `DB_HISTORY.md` detailing operational (SQLite WAL) and reasoning schema architectures.
  4. Implement `THOUGHT_LOGS.md` establishing the logging protocol.
  5. Run unit/integration tests to ensure no regressions occur.
- **Verification Vector**:
  - Run the fast pytest test suite in WSL (`.venv/bin/pytest -m "not (integration or ai_generated)" --tb=short`).
  - Verify that the compiled static assets and reverse proxy routes continue to behave cleanly.

---

## 🛠️ 3. Debugging Guidelines for Developers & Agents

When debugging Cherenkov components:

1. **Verify Backend Status**:
   ```bash
   # Run the FastAPI server in hot-reload mode
   uvicorn packages.cherenkov.api.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Verify Threaded Proxy Tunnel**:
   ```bash
   # Run the custom HTTP and WebSocket proxy serving the compiled dashboard
   python3 proxy_server.py
   ```

3. **Inspect the Local SQL Database**:
   ```bash
   # Query pending approvals awaiting HITL action
   sqlite3 ~/.cherenkov/results.db "SELECT * FROM findings_pending WHERE status='pending';"
   ```

4. **Verify Cognitive Integrity**:
   ```bash
   # Run the reasoning store anchor verification script
   python3 -c "from cherenkov.core.reasoning_store import ReasoningStore; from pathlib import Path; store = ReasoningStore(Path.home() / '.cherenkov' / 'reasoning.db'); store.verify('test_session')"
   ```
