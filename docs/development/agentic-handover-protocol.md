# Agentic Handover Protocol

This protocol defines how CHERENKOV agents transition work between each other to maintain consistency, safety, and architectural integrity.

## The C2 Hub (Control Tower)

The C2 Hub is the central coordination layer. Any agent can assume the C2 role to act as the primary coordinator for a session or workflow.

### Coordination Levels (3-tier Alert System)

Agents monitor their own context usage and status to trigger handovers:

1.  **🟢 GREEN (< 75% Context):** Normal operations. Agent is stable.
2.  **🟡 YELLOW (75-90% Context):** Approaching context limits. Agent should begin preparing a Handover Packet and notify the C2 Hub.
3.  **🔴 RED (> 90% Context):** Critical threshold. Agent MUST stop work, serialize state to the `AgentStateStore`, and trigger an immediate handover to a fresh agent.

## Handover Packet

A formal Handover Packet (serialized as a `HandoverSnapshot`) must include:

-   **Context Summary:** Brief description of current progress and goal.
-   **Accumulated Results:** Data gathered or produced so far.
-   **Active Task ID:** The ID of the task currently being executed.
-   **Status & Version:** Current agent status and state version.
-   **Capabilities Needed:** List of capabilities required to continue the work.

## Handover Process

1.  **Initiation:** The source agent (or C2 Hub) calls `initiate_handover`.
2.  **Snapshot Creation:** Source agent state is captured in a `HandoverSnapshot`.
3.  **Target Ready:** The target agent is notified and enters `RECEIVING_HANDOFF` status.
4.  **Acceptance:** Target agent validates the snapshot against its capabilities.
5.  **Completion:** Target agent calls `complete_handover`, absorbing the snapshot state and becoming `READY`.
6.  **Cleanup:** Source agent returns to `IDLE` or is terminated.

## AgentStateStore

The `AgentStateStore` is the single source of truth for agent persistence.
-   Located in `agent_state/` (JSON backend).
-   Supports `Redis` for distributed environments.
-   Provides optimistic concurrency via versioning.

## Code of Conduct for Agents

1.  **Read-SSOT First:** Every agent MUST read `.agents/context.md` before performing any action.
2.  **No Hidden State:** All relevant state MUST be stored in `AgentState` or the project filesystem.
3.  **Atomic Handovers:** Work MUST NOT be lost during transitions.
4.  **Acknowledge C2:** All agents operate under the coordination of the current C2 Hub role holder.
