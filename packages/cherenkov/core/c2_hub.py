"""
C2 Hub (Control Tower) - Agent-agnostic coordination layer.

The C2 Hub is the central coordination point for all CHERENKOV agents.
It manages:
- The Single Source of Truth (SSOT) for project context.
- Agent lifecycle and state transitions via AgentStateStore.
- The Agentic Handover Protocol (Green/Yellow/Red alerts).
- Cross-functional coordination between specialized agents (Jules, Antigravity, etc.).

Any agent can "assume" the C2 Hub role to act as the primary coordinator.
"""

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from cherenkov.core.agent_state_store import AgentState, AgentStatus, AgentStateStore, default_state_store

logger = logging.getLogger(__name__)


class C2Hub:
    """
    The Control Tower for agentic coordination.
    """

    def __init__(self, ssot_path: str = ".agents/context.md", state_store: Optional[AgentStateStore] = None):
        self.ssot_path = Path(ssot_path)
        self.state_store = state_store or default_state_store()
        self._active_c2_agent_id: Optional[str] = None

    def get_ssot_content(self) -> str:
        """Read the current Single Source of Truth."""
        if not self.ssot_path.exists():
            logger.warning(f"SSOT file not found at {self.ssot_path}")
            return ""
        return self.ssot_path.read_text(encoding="utf-8")

    def update_ssot(self, content: str, agent_id: str) -> bool:
        """Update the SSOT. Only allowed by the active C2 agent or with authorization."""
        try:
            # In a more strict implementation, we would check if agent_id is the active C2 agent
            self.ssot_path.parent.mkdir(parents=True, exist_ok=True)
            self.ssot_path.write_text(content, encoding="utf-8")
            logger.info(f"SSOT updated by agent {agent_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update SSOT: {e}")
            return False

    def assume_c2_role(self, agent_id: str) -> bool:
        """Set an agent as the active C2 coordinator."""
        state = self.state_store.get(agent_id)
        if not state:
            logger.error(f"Cannot assume C2 role: Agent {agent_id} not found in state store.")
            return False

        self._active_c2_agent_id = agent_id
        logger.info(f"Agent {agent_id} ({state.role}) has assumed the C2 Hub role.")
        return True

    def get_active_c2_agent(self) -> Optional[AgentState]:
        """Get the state of the current C2 coordinator."""
        if not self._active_c2_agent_id:
            return None
        return self.state_store.get(self._active_c2_agent_id)

    def initiate_handover(self, source_agent_id: str, target_agent_id: str, reason: str) -> Optional[str]:
        """
        Initiate a formal handover between two agents.
        Returns the snapshot_id if successful.
        """
        source_state = self.state_store.get(source_agent_id)
        target_state = self.state_store.get(target_agent_id)

        if not source_state or not target_state:
            logger.error("Handover failed: Source or target agent not found.")
            return None

        logger.info(f"Initiating handover: {source_agent_id} -> {target_agent_id} (Reason: {reason})")

        # Create snapshot
        snapshot = source_state.create_handoff_snapshot(target_agent_id, reason=reason)
        
        # Update states
        source_state.status = AgentStatus.HANDING_OFF
        target_state.status = AgentStatus.RECEIVING_HANDOFF
        
        self.state_store.update(source_state)
        self.state_store.update(target_state)
        self.state_store.save_handoff(snapshot)

        return snapshot.snapshot_id

    def complete_handover(self, snapshot_id: str) -> bool:
        """Complete a pending handover."""
        snapshot = self.state_store.load_handoff(snapshot_id)
        if not snapshot:
            logger.error(f"Handover completion failed: Snapshot {snapshot_id} not found.")
            return False

        source_state = self.state_store.get(snapshot.source_agent_id)
        target_state = self.state_store.get(snapshot.target_agent_id)

        if not target_state:
            logger.error(f"Handover completion failed: Target agent {snapshot.target_agent_id} not found.")
            return False

        # Apply snapshot to target state
        target_state.context.update(snapshot.context)
        target_state.accumulated_results.update(snapshot.accumulated_results)
        target_state.current_workflow_id = snapshot.workflow_id
        target_state.current_task_id = snapshot.task_id
        target_state.status = AgentStatus.READY
        
        snapshot.mark_accepted()
        
        if source_state:
            source_state.status = AgentStatus.IDLE
            self.state_store.update(source_state)
        
        self.state_store.update(target_state)
        self.state_store.save_handoff(snapshot)

        logger.info(f"Handover {snapshot_id} completed successfully.")
        return True

    def get_hub_status(self) -> Dict[str, Any]:
        """Get an overview of the C2 Hub status."""
        active_c2 = self.get_active_c2_agent()
        all_agents = []
        
        # This is a bit inefficient if there are many agents, but okay for now
        for agent_id in self.state_store.backend.list_all():
            state = self.state_store.get(agent_id)
            if state:
                all_agents.append({
                    "agent_id": state.agent_id,
                    "role": state.role,
                    "status": state.status,
                    "updated_at": state.updated_at
                })

        return {
            "active_c2_agent": active_c2.agent_id if active_c2 else None,
            "ssot_path": str(self.ssot_path),
            "ssot_last_modified": datetime.fromtimestamp(self.ssot_path.stat().st_mtime, tz=timezone.utc).isoformat() if self.ssot_path.exists() else None,
            "agents": all_agents,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


_default_hub: Optional[C2Hub] = None

def default_c2_hub() -> C2Hub:
    """Get the default global C2Hub instance."""
    global _default_hub
    if _default_hub is None:
        _default_hub = C2Hub()
    return _default_hub
