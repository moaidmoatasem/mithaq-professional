# CHERENKOV System Design & Architecture

This document provides both the High Level Design (HLD) and Low Level Design (LLD) for the CHERENKOV Sovereign Security platform.

## 1. High Level Design (HLD)

### 1.1 The Trident Architecture
CHERENKOV operates on a mathematically provable framework designed to prevent data egress and guarantee finding validity.

*   **DAREE3 (The Shield):** A fail-closed network perimeter. It sits at the Docker/Nginx layer, proxying requests and strictly dropping outbound connections not whitelisted for local telemetry.
*   **SIYAADA (Sovereignty):** The data redaction engine. In hybrid configurations (where some processing occurs off-node), SIYAADA strips all PII, API keys, and proprietary code before leaving the node. It uses a bidirectional mapping (`RedactionMap`) for safe re-hydration.
*   **AL-BURHAN (The Proof):** The validation sandbox. Security findings are only escalated if AL-BURHAN can successfully execute a non-destructive Proof of Concept (PoC) against the local target. It outputs cryptographic signatures (Shred Receipts) of the execution.

### 1.2 Multi-Agent Swarm
The system uses multiple AI agents to perform complex reasoning, orchestrated to prevent context poisoning:
*   **Al-Muhandis (Strategist):** High-level attack planning.
*   **Al-Munafeedh (Executor):** Runs local security scripts and scanners.
*   **Al-Hakam (Arbiter):** Oversees agent interaction and enforces AIMD circuit breakers.
*   **Al-Hafiz (Memory):** Qdrant-backed RAG system for CVEs and Arabic dialect processing.

## 2. Low Level Design (LLD)

### 2.1 Agent State Management
Agents maintain a state vector to allow the orchestrator to load balance and detect faults.
```python
class AgentState(BaseModel):
    id: str
    cognitive_load: float  # Current load (0.0 - 1.0)
    active_missions: List[str]
    last_trace_id: Optional[str]
    circuit_breaker_status: str  # OPEN, HALF_OPEN, CLOSED
```

### 2.2 Orchestration Flow
The `HybridOrchestrator` handles the handover between agents.
1.  **Input:** User provides target (URL/APK).
2.  **Strategy:** *Al-Muhandis* generates an attack chain schema.
3.  **Sanitization:** The schema is validated; inputs sanitized.
4.  **Execution:** *Al-Munafeedh* executes the tools based on the schema.
5.  **Validation:** Findings are sent to *Al-Burhan* for execution in an isolated container.
6.  **Human-in-the-Loop:** If the finding is CRITICAL, execution pauses and requires a cryptographically signed approval from a human operator.
7.  **Finalization:** A `BurhanTrace` is generated, WORM logged, and presented to the UI.

### 2.3 BurhanTrace (Evidence Schema)
```python
class BurhanTrace(BaseModel):
    timestamp: datetime
    finding_id: str
    poc_binary: bytes  # Retained only locally
    execution_log: str
    signature: str  # SHA-256(poc_binary + execution_log)
```

### 2.4 Communication Protocol
Agents communicate via local HTTP REST APIs with strict rate limiting. If an agent (e.g., local LLM) fails, the AIMD (Additive Increase Multiplicative Decrease) circuit breaker opens, halving the request rate, and slowly increasing it upon success.
