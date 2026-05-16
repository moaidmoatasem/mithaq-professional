# Swarm Orchestrator

The Swarm Orchestrator manages the lifecycle of the multi-agent cognitive swarm, coordinating between the Trident components and AI agent nodes.

## Architecture

The orchestrator is the central coordinator. It receives scan requests, delegates to the Agent Governor, and aggregates results.

## Key Components

| Component | Responsibility |
|---|---|
| **Orchestrator API** | HTTP/WS entry point for all client requests |
| **Agent Governor** | Routes tasks, manages state, enforces data access |
| **Circuit Breaker** | AIMD-based failure prevention (3-retry limit per agent) |
| **Session Manager** | End-to-end encrypted communication channels |

## Agent State Management

Each agent maintains a state vector for load balancing and fault detection:

```python
class AgentState(BaseModel):
    id: str
    cognitive_load: float         # Current load (0.0 - 1.0)
    active_missions: List[str]
    last_trace_id: Optional[str]
    circuit_breaker_status: str   # OPEN, HALF_OPEN, CLOSED
```

## Execution Flow

1. Client submits scan → Orchestrator API
2. TENSOR generates attack chain schema
3. Schema validated, inputs sanitized via ABLATION
4. KINETIC executes scanners based on schema
5. Findings sent to TOKAMAK for sandbox validation
6. If CRITICAL → HITL pause for human approval
7. BurhanTrace generated, WORM logged, presented to UI

## AIMD Circuit Breaker

When an agent API fails, the request rate is halved immediately. When requests succeed, the rate increases linearly. This prevents cascading failures when local LLM inference is overwhelmed.

For complete implementation details, see [System Design & State Machine](../pm/SYSTEM_DESIGN.md) and [Design Patterns](../pm/DESIGN_PATTERNS_BEST_PRACTICES.md).
