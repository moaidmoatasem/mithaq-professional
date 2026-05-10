"""
Capability Registry & Capacity Control - Agent discovery and dynamic capacity management.

Provides:
- CapabilityRegistry: Register and discover agents by what they can do
- AIMDCapacityController: Additive-Increase/Multiplicative-Decrease capacity control
   (reused and generalized from HybridOrchestrator pattern)
- DelegationPolicy: Policies for when delegation is allowed
- SelectionStrategy: How to select among multiple capable agents

Integrates with:
- AgentStateStore: For getting current agent availability
- EventBus: For capability announcements and queries
"""

import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from cherenkov.core.agent_state_store import (
    AgentStateStore,
    AgentStatus,
    default_state_store,
)

logger = logging.getLogger(__name__)


class SelectionStrategy(str, Enum):
    """Strategies for selecting among multiple capable agents."""

    FIRST_AVAILABLE = "first_available"
    ROUND_ROBIN = "round_robin"
    LEAST_BUSY = "least_busy"
    HIGHEST_CAPACITY = "highest_capacity"
    RANDOM = "random"


class SelectionPriority(str, Enum):
    """Priority factors for agent selection."""

    LOCAL_EXECUTION = "local"
    COST_EFFICIENCY = "cost"
    SPEED = "speed"
    SPECIALIZATION = "specialization"
    ANY = "any"


@dataclass
class AgentRegistration:
    """Registration record for an agent in the capability registry.

    Tracks what an agent can do and how to reach it.
    """

    agent_id: str
    role: str
    capabilities: List[str]

    endpoint: Optional[str] = None
    is_local: bool = True
    priority_score: float = 0.5
    metadata: Dict[str, Any] = field(default_factory=dict)

    registered_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    last_heartbeat_at: Optional[str] = None
    is_active: bool = True


@dataclass
class DelegationPolicy:
    """
    Policy governing when delegation is allowed.

    Used by DelegationGuardrails to make go/no-go decisions.
    """

    allow_delegation: bool = True
    max_delegation_depth: int = 3
    require_acknowledgment: bool = True
    require_capability_match: bool = True
    allow_same_role_delegation: bool = False

    allowed_capabilities: Optional[List[str]] = None
    forbidden_capabilities: Optional[List[str]] = None

    min_agents_for_selection: int = 1

    def can_delegate_to_capability(self, capability: str) -> bool:
        """Check if delegation to a capability is allowed by policy.

        Args:
            capability: The capability being delegated

        Returns:
            True if allowed, False otherwise
        """
        if not self.allow_delegation:
            return False

        if self.forbidden_capabilities and capability in self.forbidden_capabilities:
            return False

        if self.allowed_capabilities and capability not in self.allowed_capabilities:
            return False

        return True

    def can_delegate_between_roles(self, source_role: str, target_role: str) -> bool:
        """Check if delegation between roles is allowed.

        Args:
            source_role: Role of delegating agent
            target_role: Role of receiving agent

        Returns:
            True if allowed, False otherwise
        """
        if not self.allow_delegation:
            return False

        if source_role == target_role and not self.allow_same_role_delegation:
            return False

        return True


def create_default_policy() -> DelegationPolicy:
    """Create a sensible default delegation policy.

    Defaults:
    - Allow delegation (obviously)
    - Max depth 3 (prevent infinite delegation chains)
    - Require capability match
    - Require acknowledgment
    - Allow same-role delegation (for load balancing)
    """
    return DelegationPolicy(
        allow_delegation=True,
        max_delegation_depth=3,
        require_acknowledgment=True,
        require_capability_match=True,
        allow_same_role_delegation=True,
    )


class AIMDCapacityController:
    """
    Additive-Increase/Multiplicative-Decrease (AIMD) capacity controller.

    Generalized from the HybridOrchestrator pattern (hybrid_orchestrator.py:210-230).

    How it works:
    - On SUCCESS: Increment consecutive success counter. After N successes, ADD capacity.
    - On FAILURE: MULTIPLICATIVELY decrease capacity (typically cut in half).
    - Minimum capacity is always 1.

    Use cases:
    - Dynamic concurrency control for API calls
    - Agent pool capacity management
    - Workflow parallelism tuning
    - Rate limit adaptation

    Attributes:
        min_capacity: Minimum allowed capacity (default 1)
        max_capacity: Maximum allowed capacity (default 32)
        success_threshold: How many successes before increasing (default 5)
        decrease_factor: Multiply capacity by this on failure (default 0.5)
    """

    def __init__(
        self,
        initial_capacity: int = 4,
        min_capacity: int = 1,
        max_capacity: int = 32,
        success_threshold: int = 5,
        decrease_factor: float = 0.5,
    ):
        self.current_capacity = initial_capacity
        self.min_capacity = min_capacity
        self.max_capacity = max_capacity
        self.success_threshold = success_threshold
        self.decrease_factor = decrease_factor

        self.consecutive_successes = 0
        self.total_successes = 0
        self.total_failures = 0

        self._lock = threading.Lock()

    def record_success(self) -> int:
        """Record a successful operation.

        After success_threshold consecutive successes, capacity is increased by 1.

        Returns:
            New capacity
        """
        with self._lock:
            self.consecutive_successes += 1
            self.total_successes += 1

            if self.consecutive_successes >= self.success_threshold:
                if self.current_capacity < self.max_capacity:
                    self.current_capacity += 1
                    logger.info(
                        f"AIMD: Increasing capacity to {self.current_capacity} "
                        f"(after {self.success_threshold} consecutive successes)"
                    )
                self.consecutive_successes = 0

            return self.current_capacity

    def record_failure(self) -> int:
        """Record a failed operation.

        Capacity is multiplicatively decreased (cut in half by default),
        but never below min_capacity.

        Returns:
            New capacity
        """
        with self._lock:
            old_capacity = self.current_capacity
            self.consecutive_successes = 0
            self.total_failures += 1

            new_capacity = max(
                self.min_capacity, int(old_capacity * self.decrease_factor)
            )

            if new_capacity != old_capacity:
                logger.warning(
                    f"AIMD: Decreasing capacity {old_capacity} -> {new_capacity} "
                    f"after failure"
                )
                self.current_capacity = new_capacity

            return self.current_capacity

    def get_capacity(self) -> int:
        """Get current capacity level (thread-safe)."""
        with self._lock:
            return self.current_capacity

    def can_acquire(self, requested: int = 1) -> bool:
        """Check if requested capacity is available.

        Args:
            requested: How much capacity is requested

        Returns:
            True if available
        """
        with self._lock:
            return requested <= self.current_capacity

    def reset(self, capacity: Optional[int] = None) -> None:
        """Reset controller state.

        Args:
            capacity: Optional new initial capacity (uses original if not specified)
        """
        with self._lock:
            if capacity is not None:
                self.current_capacity = capacity
            self.consecutive_successes = 0

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about controller performance."""
        with self._lock:
            return {
                "current_capacity": self.current_capacity,
                "min_capacity": self.min_capacity,
                "max_capacity": self.max_capacity,
                "consecutive_successes": self.consecutive_successes,
                "success_threshold": self.success_threshold,
                "total_successes": self.total_successes,
                "total_failures": self.total_failures,
                "decrease_factor": self.decrease_factor,
            }


class CapabilityRegistry:
    """
    Central registry for agent capabilities.

    Allows:
    - Registering agents with their capabilities
    - Discovering agents that can perform specific tasks
    - Selecting the best agent for a task based on strategy
    - Heartbeat-based liveness tracking

    Integrates with AgentStateStore for availability checks.
    """

    def __init__(
        self,
        state_store: Optional[AgentStateStore] = None,
        selection_strategy: SelectionStrategy = SelectionStrategy.LEAST_BUSY,
    ):
        self._agents: Dict[str, AgentRegistration] = {}
        self._capability_index: Dict[str, List[str]] = {}
        self._round_robin_counters: Dict[str, int] = {}
        self._state_store = state_store or default_state_store()
        self._selection_strategy = selection_strategy
        self._lock = threading.Lock()

    def register(self, registration: AgentRegistration) -> None:
        """Register an agent and its capabilities.

        Args:
            registration: AgentRegistration with capabilities
        """
        with self._lock:
            agent_id = registration.agent_id

            if agent_id in self._agents:
                old_caps = self._agents[agent_id].capabilities
                for cap in old_caps:
                    if cap in self._capability_index and agent_id in self._capability_index[cap]:
                        self._capability_index[cap].remove(agent_id)

            self._agents[agent_id] = registration

            for cap in registration.capabilities:
                if cap not in self._capability_index:
                    self._capability_index[cap] = []
                if agent_id not in self._capability_index[cap]:
                    self._capability_index[cap].append(agent_id)

            logger.info(
                f"Registered agent {agent_id} (role={registration.role}) "
                f"with capabilities: {registration.capabilities}"
            )

    def unregister(self, agent_id: str) -> bool:
        """Remove an agent from the registry.

        Args:
            agent_id: Agent to unregister

        Returns:
            True if agent was found and removed
        """
        with self._lock:
            if agent_id not in self._agents:
                return False

            registration = self._agents[agent_id]

            for cap in registration.capabilities:
                if cap in self._capability_index and agent_id in self._capability_index[cap]:
                    self._capability_index[cap].remove(agent_id)

            del self._agents[agent_id]

            logger.info(f"Unregistered agent {agent_id}")
            return True

    def heartbeat(self, agent_id: str) -> bool:
        """Record a heartbeat from an agent.

        Resets inactivity tracking and marks as active.

        Args:
            agent_id: Agent sending heartbeat

        Returns:
            True if agent is registered
        """
        with self._lock:
            if agent_id not in self._agents:
                return False

            self._agents[agent_id].last_heartbeat_at = datetime.now(
                timezone.utc
            ).isoformat()
            self._agents[agent_id].is_active = True
            return True

    def find_agents_for_capability(
        self,
        capability: str,
        include_unavailable: bool = False,
    ) -> List[AgentRegistration]:
        """Find all agents that have a specific capability.

        Args:
            capability: Capability to look for
            include_unavailable: Include agents not marked available in AgentStateStore

        Returns:
            List of AgentRegistration for matching agents
        """
        with self._lock:
            agent_ids = self._capability_index.get(capability, [])

            results = []
            for agent_id in agent_ids:
                if agent_id not in self._agents:
                    continue

                registration = self._agents[agent_id]

                if not registration.is_active:
                    continue

                if not include_unavailable:
                    state = self._state_store.get(agent_id)
                    if state and not state.is_available_for_delegation():
                        continue

                results.append(registration)

            return results

    def select_agent(
        self,
        capability: str,
        strategy: Optional[SelectionStrategy] = None,
    ) -> Optional[AgentRegistration]:
        """Select the best agent for a capability using selection strategy.

        Args:
            capability: Required capability
            strategy: Optional override of default strategy

        Returns:
            Selected AgentRegistration or None if no agent available
        """
        candidates = self.find_agents_for_capability(capability)

        if not candidates:
            return None

        if len(candidates) == 1:
            return candidates[0]

        strategy = strategy or self._selection_strategy

        with self._lock:
            if strategy == SelectionStrategy.FIRST_AVAILABLE:
                return candidates[0]

            elif strategy == SelectionStrategy.LEAST_BUSY:
                return self._select_least_busy(candidates)

            elif strategy == SelectionStrategy.ROUND_ROBIN:
                return self._select_round_robin(capability, candidates)

            elif strategy == SelectionStrategy.HIGHEST_CAPACITY:
                candidates.sort(key=lambda r: r.priority_score, reverse=True)
                return candidates[0]

            else:
                return candidates[0]

    def _select_least_busy(
        self,
        candidates: List[AgentRegistration],
    ) -> AgentRegistration:
        """Select the least busy agent based on AgentStateStore status."""
        best = None
        best_priority = -1

        status_priority = {
            AgentStatus.IDLE: 4,
            AgentStatus.READY: 3,
            AgentStatus.WAITING: 2,
            AgentStatus.RUNNING: 1,
        }

        for candidate in candidates:
            state = self._state_store.get(candidate.agent_id)
            if state is None:
                priority = 0
            else:
                priority = status_priority.get(state.status, 0)

            if priority > best_priority:
                best_priority = priority
                best = candidate

        return best or candidates[0]

    def _select_round_robin(
        self,
        capability: str,
        candidates: List[AgentRegistration],
    ) -> AgentRegistration:
        """Select agent using round-robin per capability."""
        if capability not in self._round_robin_counters:
            self._round_robin_counters[capability] = 0

        idx = self._round_robin_counters[capability]
        selected = candidates[idx % len(candidates)]
        self._round_robin_counters[capability] = (idx + 1) % len(candidates)
        return selected

    def get_all_capabilities(self) -> List[str]:
        """Get all registered capability names."""
        with self._lock:
            return list(self._capability_index.keys())

    def get_registration(self, agent_id: str) -> Optional[AgentRegistration]:
        """Get registration for a specific agent."""
        with self._lock:
            return self._agents.get(agent_id)

    def list_all_agents(self) -> List[AgentRegistration]:
        """List all registered agents."""
        with self._lock:
            return list(self._agents.values())


_default_registry: Optional[CapabilityRegistry] = None


def default_capability_registry() -> CapabilityRegistry:
    """Get the default global CapabilityRegistry instance."""
    global _default_registry
    if _default_registry is None:
        _default_registry = CapabilityRegistry()
    return _default_registry


_default_aimd: Optional[AIMDCapacityController] = None


def default_aimd_controller() -> AIMDCapacityController:
    """Get the default global AIMDCapacityController instance."""
    global _default_aimd
    if _default_aimd is None:
        _default_aimd = AIMDCapacityController()
    return _default_aimd
