# CHERENKOV Development Plan

This document breaks down the development phases into actionable sprints for AI agents and human developers.

## Guiding Principle
**Test-Driven Development (TDD) is mandatory.** Write the test, run the test (it should fail), write the code, run the test (it should pass), then refactor.

## Sprint 1: Formalize Scanners (Current)
**Goal:** Migrate candidate scanners to a uniform interface.
1. **Task:** Define `BaseScanner` abstract class in `src/cherenkov/scanners/base.py`.
2. **Task:** Refactor `cherenkov_simple_scanner.py` to inherit from `BaseScanner`.
3. **Task:** Implement unit tests for the base interface ensuring strict input/output validation.
4. **Autonomy Level:** Fully autonomous.

## Sprint 2: Parallel Orchestration Core
**Goal:** Refactor the orchestrator to support concurrent execution.
1. **Task:** Update `ai_workflows_orchestrator.py` to use `asyncio` for executing agent tasks concurrently.
2. **Task:** Implement AIMD circuit breaker logic for agent calls.
3. **Task:** Write integration tests proving parallel execution finishes faster than sequential execution without errors.
4. **Autonomy Level:** Fully autonomous.

## Sprint 3: The Validation Sandbox (TOKAMAK)
**Goal:** Implement the isolated execution environment for PoCs.
1. **Task:** Create Docker definitions for the TOKAMAK sandbox (minimal, no network).
2. **Task:** Implement the `Command` pattern for sending payloads to the sandbox.
3. **Task:** Implement cryptographic signing of the execution results (BurhanTrace).
4. **Autonomy Level:** Human Review Required (Security Architecture).

## Sprint 4: Human-in-the-Loop (HITL) Workflows
**Goal:** Ensure critical actions cannot be performed without human consent.
1. **Task:** Implement an API endpoint to pause workflow execution pending approval.
2. **Task:** Update UI to present pending approvals.
3. **Task:** Implement RBAC to verify the approving user has sufficient clearance.
4. **Autonomy Level:** Human Review Required (Core Security Feature).

## Sprint 5: Compliance and Reporting
**Goal:** Map findings to regulatory frameworks.
1. **Task:** Build the compliance mapping engine (CVE/CWE -> SAMA/EGY-FIN).
2. **Task:** Integrate local PDF generation for audit reports.
3. **Autonomy Level:** Fully autonomous.
