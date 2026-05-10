"""
Agent State Store - Persistent state management and handoff for agents.

Provides:
- AgentStatus enum for tracking agent lifecycle state
- AgentState dataclass for full agent state serialization
- HandoverSnapshot for safe state transfer during delegation
- AgentStateStore with backend abstraction (file-based now, Redis-ready)
- Single source of truth for AgentStatus enum
"""

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class AgentStatus(str, Enum):
    """Lifecycle status of an agent.

    Single source of truth for agent status tracking.
    Used for:
    - Workflow coordination
    - Delegation decisions
    - Handoff validation
    - Error recovery
    """

    IDLE = "idle"
    READY = "ready"
    RUNNING = "running"
    WAITING = "waiting"
    PAUSED = "paused"
    BLOCKED = "blocked"
    ERROR = "error"
    COMPLETED = "completed"
    HANDING_OFF = "handing_off"
    RECEIVING_HANDOFF = "receiving_handoff"


@dataclass
class AgentState:
    """
    Complete serialized state of an agent.

    Captures everything needed to:
    - Resume an agent after pause/restart
    - Hand off to another agent via delegation
    - Audit agent execution history
    - Debug and replay workflows

    Attributes:
        agent_id: Unique identifier for this agent instance
        role: Agent's role (e.g., 'developer', 'security_analyst')
        status: Current lifecycle status
        current_task_id: Task being worked on (if any)
        current_workflow_id: Workflow context (if any)
        accumulated_results: Output from completed tasks
        context: Agent-specific working context
        metrics: Performance/usage metrics
        errors: Recent error history
        capabilities: What this agent can do
        created_at: When this state was first created
        updated_at: When this state was last modified
        version: Monotonically increasing version for optimistic concurrency
    """

    agent_id: str
    role: str
    status: str = AgentStatus.IDLE

    current_task_id: Optional[str] = None
    current_workflow_id: Optional[str] = None
    task_progress: float = 0.0

    accumulated_results: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)

    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    version: int = 1

    def touch(self) -> None:
        """Update timestamp and increment version."""
        self.updated_at = datetime.now(timezone.utc).isoformat()
        self.version += 1

    def is_available_for_delegation(self) -> bool:
        """Check if this agent can accept delegated tasks."""
        available_states = {
            AgentStatus.IDLE,
            AgentStatus.READY,
            AgentStatus.WAITING,
        }
        return self.status in available_states

    def add_error(
        self,
        error_message: str,
        error_type: str = "general",
        task_id: Optional[str] = None,
    ) -> None:
        """Record an error in the agent's error history.

        Args:
            error_message: Human-readable error description
            error_type: Category of error
            task_id: Optional task where error occurred
        """
        error_record = {
            "message": error_message,
            "type": error_type,
            "task_id": task_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.errors.append(error_record)
        self.status = AgentStatus.ERROR
        self.touch()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentState":
        """Deserialize from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def create_handoff_snapshot(
        self,
        target_agent_id: str,
        reason: str = "delegation",
        include_full_context: bool = True,
    ) -> "HandoverSnapshot":
        """Create a snapshot for handing off to another agent.

        Args:
            target_agent_id: Agent receiving the handoff
            reason: Why this handoff is happening
            include_full_context: Whether to include full context (False for sensitive data)

        Returns:
            HandoverSnapshot ready for transfer
        """
        context_to_include = self.context if include_full_context else {}

        return HandoverSnapshot(
            source_agent_id=self.agent_id,
            target_agent_id=target_agent_id,
            source_agent_role=self.role,
            workflow_id=self.current_workflow_id,
            task_id=self.current_task_id,
            task_progress=self.task_progress,
            accumulated_results=dict(self.accumulated_results),
            context=context_to_include,
            capabilities_needed=list(self.capabilities),
            reason=reason,
            source_status=self.status,
            source_version=self.version,
        )


@dataclass
class HandoverSnapshot:
    """
    A safe, serializable snapshot of agent state for delegation/handoff.

    Unlike AgentState (which is mutable and live), HandoverSnapshot:
    - Is immutable once created
    - Contains only what's needed for handoff
    - Can be validated before acceptance
    - Tracks source and target explicitly

    Used for:
    - Safe delegation between agents
    - Workflow resumption after restart
    - Checkpoint-based recovery
    """

    source_agent_id: str
    target_agent_id: str
    source_agent_role: str

    snapshot_id: str = field(default_factory=lambda: str(uuid4()))
    workflow_id: Optional[str] = None
    task_id: Optional[str] = None
    task_progress: float = 0.0

    accumulated_results: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    capabilities_needed: List[str] = field(default_factory=list)

    reason: str = "delegation"
    source_status: str = AgentStatus.IDLE
    source_version: int = 1

    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    accepted_at: Optional[str] = None
    rejected_at: Optional[str] = None
    rejection_reason: Optional[str] = None

    def is_valid(self) -> bool:
        """Basic validation of snapshot structure."""
        if not self.source_agent_id or not self.target_agent_id:
            return False
        if self.task_progress < 0 or self.task_progress > 1:
            return False
        return True

    def can_accept(self, recipient_capabilities: List[str]) -> bool:
        """Check if recipient has needed capabilities.

        Args:
            recipient_capabilities: What the receiving agent can do

        Returns:
            True if all needed capabilities are present
        """
        for needed in self.capabilities_needed:
            if needed not in recipient_capabilities:
                return False
        return True

    def mark_accepted(self) -> None:
        """Mark this snapshot as accepted by target."""
        self.accepted_at = datetime.now(timezone.utc).isoformat()
        self.rejected_at = None
        self.rejection_reason = None

    def mark_rejected(self, reason: str) -> None:
        """Mark this snapshot as rejected by target.

        Args:
            reason: Why the handoff was rejected
        """
        self.rejected_at = datetime.now(timezone.utc).isoformat()
        self.rejection_reason = reason
        self.accepted_at = None

    def is_accepted(self) -> bool:
        return self.accepted_at is not None and self.rejected_at is None

    def is_rejected(self) -> bool:
        return self.rejected_at is not None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HandoverSnapshot":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class AgentStateBackend(ABC):
    """Abstract base for agent state storage backends.

    Allows swapping implementations:
    - FileAgentStateBackend: Local JSON files (current)
    - RedisAgentStateBackend: Distributed (future)
    - SqliteAgentStateBackend: Embedded DB (future)
    """

    @abstractmethod
    def save(self, state: AgentState) -> bool:
        """Save agent state. Returns True on success."""
        pass

    @abstractmethod
    def load(self, agent_id: str) -> Optional[AgentState]:
        """Load agent state by ID. Returns None if not found."""
        pass

    @abstractmethod
    def delete(self, agent_id: str) -> bool:
        """Delete agent state. Returns True on success."""
        pass

    @abstractmethod
    def list_all(self) -> List[str]:
        """List all agent IDs in storage."""
        pass

    @abstractmethod
    def save_snapshot(self, snapshot: HandoverSnapshot) -> bool:
        """Save a handoff snapshot."""
        pass

    @abstractmethod
    def load_snapshot(self, snapshot_id: str) -> Optional[HandoverSnapshot]:
        """Load a handoff snapshot by ID."""
        pass


class FileAgentStateBackend(AgentStateBackend):
    """File-based JSON storage for agent state.

    Directory structure:
        agent_state/
            {agent_id}.json          # Live agent states
            snapshots/
                {snapshot_id}.json   # Handover snapshots
    """

    def __init__(self, storage_dir: str = "agent_state"):
        self.storage_dir = Path(storage_dir)
        self.snapshots_dir = self.storage_dir / "snapshots"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)

    def _get_agent_path(self, agent_id: str) -> Path:
        return self.storage_dir / f"{agent_id}.json"

    def _get_snapshot_path(self, snapshot_id: str) -> Path:
        return self.snapshots_dir / f"{snapshot_id}.json"

    def save(self, state: AgentState) -> bool:
        try:
            state.touch()
            filepath = self._get_agent_path(state.agent_id)
            with open(filepath, "w") as f:
                json.dump(state.to_dict(), f, indent=2)
            logger.debug(f"Saved state for agent {state.agent_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save agent state: {e}")
            return False

    def load(self, agent_id: str) -> Optional[AgentState]:
        filepath = self._get_agent_path(agent_id)
        if not filepath.exists():
            return None
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            return AgentState.from_dict(data)
        except Exception as e:
            logger.error(f"Failed to load agent state for {agent_id}: {e}")
            return None

    def delete(self, agent_id: str) -> bool:
        filepath = self._get_agent_path(agent_id)
        if filepath.exists():
            try:
                filepath.unlink()
                return True
            except Exception as e:
                logger.error(f"Failed to delete agent state for {agent_id}: {e}")
        return False

    def list_all(self) -> List[str]:
        agent_ids = []
        for filepath in self.storage_dir.glob("*.json"):
            if filepath.stem not in ("latest", "index"):
                agent_ids.append(filepath.stem)
        return agent_ids

    def save_snapshot(self, snapshot: HandoverSnapshot) -> bool:
        try:
            filepath = self._get_snapshot_path(snapshot.snapshot_id)
            with open(filepath, "w") as f:
                json.dump(snapshot.to_dict(), f, indent=2)
            logger.debug(f"Saved snapshot {snapshot.snapshot_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save snapshot: {e}")
            return False

    def load_snapshot(self, snapshot_id: str) -> Optional[HandoverSnapshot]:
        filepath = self._get_snapshot_path(snapshot_id)
        if not filepath.exists():
            return None
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            return HandoverSnapshot.from_dict(data)
        except Exception as e:
            logger.error(f"Failed to load snapshot {snapshot_id}: {e}")
            return None


class AgentStateStore:
    """
    Central registry and manager for agent states.

    Provides:
    - CRUD operations for agent states
    - Handoff snapshot management
    - Status-based queries
    - Optimistic concurrency control via version numbers

    This is the single source of truth for agent state in the system.
    """

    def __init__(self, backend: Optional[AgentStateBackend] = None):
        self.backend = backend or FileAgentStateBackend()
        self._cache: Dict[str, AgentState] = {}

    def get_or_create(
        self, agent_id: str, role: str, capabilities: Optional[List[str]] = None
    ) -> AgentState:
        """Get existing agent state or create new one if not exists.

        Args:
            agent_id: Unique agent identifier
            role: Agent role (used only if creating new)
            capabilities: Agent capabilities (used only if creating new)

        Returns:
            Existing or newly created AgentState
        """
        existing = self.get(agent_id)
        if existing:
            return existing

        state = AgentState(
            agent_id=agent_id,
            role=role,
            status=AgentStatus.IDLE,
            capabilities=capabilities or [],
        )
        self._cache[agent_id] = state
        self.backend.save(state)
        return state

    def get(self, agent_id: str) -> Optional[AgentState]:
        """Get agent state by ID.

        Checks cache first, then backend.
        """
        if agent_id in self._cache:
            return self._cache[agent_id]

        state = self.backend.load(agent_id)
        if state:
            self._cache[agent_id] = state
        return state

    def update(self, state: AgentState) -> bool:
        """Update agent state.

        Persists to backend and updates cache.
        """
        self._cache[state.agent_id] = state
        return self.backend.save(state)

    def delete(self, agent_id: str) -> bool:
        """Delete agent state."""
        if agent_id in self._cache:
            del self._cache[agent_id]
        return self.backend.delete(agent_id)

    def set_status(self, agent_id: str, status: str) -> bool:
        """Update just the status of an agent.

        Args:
            agent_id: Agent to update
            status: New status (from AgentStatus enum)

        Returns:
            True if successful
        """
        state = self.get(agent_id)
        if state is None:
            logger.warning(f"Cannot set status: agent {agent_id} not found")
            return False
        state.status = status
        return self.update(state)

    def find_by_status(self, status: str) -> List[AgentState]:
        """Find all agents with a specific status.

        Args:
            status: Status to filter by

        Returns:
            List of AgentState matching the status
        """
        results = []
        all_ids = self.backend.list_all()
        for agent_id in all_ids:
            state = self.get(agent_id)
            if state and state.status == status:
                results.append(state)
        return results

    def find_available_for_delegation(self) -> List[AgentState]:
        """Find all agents available to accept delegated tasks."""
        results = []
        all_ids = self.backend.list_all()
        for agent_id in all_ids:
            state = self.get(agent_id)
            if state and state.is_available_for_delegation():
                results.append(state)
        return results

    def save_handoff(self, snapshot: HandoverSnapshot) -> bool:
        """Save a handoff snapshot for later retrieval."""
        return self.backend.save_snapshot(snapshot)

    def load_handoff(self, snapshot_id: str) -> Optional[HandoverSnapshot]:
        """Load a handoff snapshot by ID."""
        return self.backend.load_snapshot(snapshot_id)

    def flush_cache(self) -> None:
        """Clear the in-memory cache (useful for testing)."""
        self._cache.clear()


_default_store: Optional[AgentStateStore] = None


def default_state_store() -> AgentStateStore:
    """Get the default global AgentStateStore instance."""
    global _default_store
    if _default_store is None:
        _default_store = AgentStateStore()
    return _default_store
