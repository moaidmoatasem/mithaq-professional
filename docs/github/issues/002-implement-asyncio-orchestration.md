---
name: "TASK: Implement Asyncio Orchestration"
about: "Migrate the orchestrator to support concurrent agent execution."
title: "[TASK] Implement Asyncio in HybridOrchestrator"
labels: ["enhancement", "sprint-2", "agent-autonomous"]
assignees: "AI-Agent-Developer"
---

## Description
The current orchestration is sequential, which drastically slows down swarm execution. We need to implement `asyncio` to allow multiple AI agents (e.g., Al-Munafeedh instances) to run security scans in parallel.

## Tasks
- [ ] Refactor `src/mithaq/ai_workflows_orchestrator.py` to use `async/await`.
- [ ] Implement a concurrency limit (semaphore) to prevent overloading the local Ollama instance.
- [ ] Update tests in `tests/` to use `pytest.mark.asyncio`.

## Constraints
- **AIMD Enforcement:** Parallel execution MUST respect the AIMD circuit breaker limits defined in `SYSTEM_DESIGN.md`. If an API times out, the semaphore limit must dynamically decrease.
- **Autonomy:** This task is autonomous, but integration tests must mathematically prove the parallel execution is faster than sequential execution before merging.
