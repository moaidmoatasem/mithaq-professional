"""
Delegation Guardrails - Policy enforcement and safety limits for agent delegation.

Provides:
- DelegationResult: Outcome of a delegation attempt
- DelegationRecord: Audit trail entry for each delegation
- DelegationGuardrails: Central policy enforcement engine with:
  - Chain depth tracking (prevent infinite delegation loops)
  - Policy validation (from DelegationPolicy)
  - Capability matching
  - Circular delegation detection

Integrates with:
- CapabilityRegistry: For agent discovery and selection
- AgentStateStore: For availability and state validation
- AgentMessageBus: For sending delegation messages
"""

import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from cherenkov.core.agent_messages import AgentMessage
from cherenkov.core.agent_state_store import (
    AgentState,
    AgentStateStore,
    AgentStatus,
    HandoverSnapshot,
    default_state_store,
)
from cherenkov.core.capability_registry import (
    AgentRegistration,
    CapabilityRegistry,
    DelegationPolicy,
    SelectionStrategy,
    create_default_policy,
    default_capability_registry,
)

logger = logging.getLogger(__name__)


class DelegationResult(str, Enum):
    """Result of a delegation attempt."""

    SUCCESS = "success"
    DECLINED = "declined"
    NO_AGENT_AVAILABLE = "no_agent_available"
    POLICY_DENIED = "policy_denied"
    CAPABILITY_MISMATCH = "capability_mismatch"
    DEPTH_LIMIT_EXCEEDED = "depth_limit_exceeded"
    CIRCULAR_DELEGATION = "circular_delegation"
    TIMEOUT = "timeout"
    ERROR = "error"


class DelegationOutcome(str, Enum):
    """Final outcome of a delegation chain."""

    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    TIMED_OUT = "timed_out"


@dataclass
class DelegationRecord:
    """
    Immutable record of a single delegation event.

    Used for:
    - Audit logging
    - Chain depth tracking
    - Circular delegation detection
    - Rollback/recovery decisions
    """

    source_agent_id: str
    source_role: str
    target_agent_id: str
    target_role: str
    workflow_id: str
    task_id: str
    capability_needed: str

    record_id: str = field(default_factory=lambda: f"dlg-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{id(threading.current_thread())}")
    result: str = DelegationResult.SUCCESS
    error_message: Optional[str] = None

    delegation_chain: List[str] = field(default_factory=list)
    handoff_snapshot_id: Optional[str] = None

    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    completed_at: Optional[str] = None
    outcome: Optional[str] = None

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        from dataclasses import asdict
        return asdict(self)

    def mark_completed(self, outcome: str, error_message: Optional[str] = None) -> None:
        """Mark this delegation as completed.

        Args:
            outcome: Final outcome from DelegationOutcome
            error_message: Optional error if failed
        """
        self.completed_at = datetime.now(timezone.utc).isoformat()
        self.outcome = outcome
        if error_message:
            self.error_message = error_message

    def get_full_chain(self) -> List[str]:
        """Get the full delegation chain including this delegation.

        Returns:
            List of agent IDs in delegation order (source first, this target last)
        """
        chain = list(self.delegation_chain) if self.delegation_chain else []
        chain.append(self.target_agent_id)
        return chain

    def get_chain_depth(self) -> int:
        """Get the current chain depth after this delegation.

        Returns:
            Number of hops including this one
        """
        return len(self.delegation_chain) + 1

    def would_cause_circular(self, candidate_target: str) -> bool:
        """Check if delegating to candidate would cause circular delegation.

        Args:
            candidate_target: Agent ID to check

        Returns:
            True if candidate is already in the chain or is the source
        """
        if candidate_target == self.source_agent_id:
            return True
        if candidate_target in self.delegation_chain:
            return True
        return False


class DelegationGuardrails:
    """
    Central policy enforcement engine for agent delegation.

    Key responsibilities:
    1. Validate delegation against policy
    2. Track chain depth (prevent infinite loops)
    3. Detect circular delegation
    4. Enforce capability matching
    5. Maintain audit trail of all delegations

    Usage:
        guardrails = DelegationGuardrails()
        result = guardrails.try_delegate(
            source_agent_id="agent-123",
            capability_needed="code_review",
            task_id="task-456",
            workflow_id="wf-789",
        )
    """

    def __init__(
        self,
        policy: Optional[DelegationPolicy] = None,
        state_store: Optional[AgentStateStore] = None,
        capability_registry: Optional[CapabilityRegistry] = None,
        selection_strategy: SelectionStrategy = SelectionStrategy.LEAST_BUSY,
    ):
        self.policy = policy or create_default_policy()
        self._state_store = state_store or default_state_store()
        self._capability_registry = capability_registry or default_capability_registry()
        self._selection_strategy = selection_strategy

        self._records: Dict[str, DelegationRecord] = {}
        self._active_chains: Dict[str, List[str]] = {}

        self._lock = threading.Lock()

    def can_delegate(
        self,
        source_agent_id: str,
        target_agent_id: str,
        capability_needed: str,
        existing_chain: Optional[List[str]] = None,
    ) -> DelegationResult:
        """
        Check if delegation is allowed WITHOUT actually performing it.

        Performs ALL checks:
        - Policy allows delegation
        - Chain depth within limit
        - Not circular
        - Capability match

        Args:
            source_agent_id: Agent wanting to delegate
            target_agent_id: Agent being considered for delegation
            capability_needed: Required capability for the task
            existing_chain: Optional existing delegation chain

        Returns:
            DelegationResult.SUCCESS if allowed, or specific error reason
        """
        chain = list(existing_chain) if existing_chain else []

        if not self.policy.allow_delegation:
            logger.warning(f"Delegation denied: policy forbids all delegation")
            return DelegationResult.POLICY_DENIED

        current_depth = len(chain)
        if current_depth >= self.policy.max_delegation_depth:
            logger.warning(
                f"Delegation denied: chain depth {current_depth} >= limit {self.policy.max_delegation_depth}"
            )
            return DelegationResult.DEPTH_LIMIT_EXCEEDED

        if target_agent_id in chain or target_agent_id == source_agent_id:
            logger.warning(
                f"Delegation denied: circular delegation detected. "
                f"Chain: {chain} -> {target_agent_id}"
            )
            return DelegationResult.CIRCULAR_DELEGATION

        if self.policy.require_capability_match:
            target_reg = self._capability_registry.get_registration(target_agent_id)
            if target_reg is None:
                logger.warning(
                    f"Delegation denied: target agent {target_agent_id} not registered"
                )
                return DelegationResult.CAPABILITY_MISMATCH

            if capability_needed not in target_reg.capabilities:
                logger.warning(
                    f"Delegation denied: target {target_agent_id} lacks capability {capability_needed}. "
                    f"Has: {target_reg.capabilities}"
                )
                return DelegationResult.CAPABILITY_MISMATCH

        target_state = self._state_store.get(target_agent_id)
        if target_state and not target_state.is_available_for_delegation():
            logger.warning(
                f"Delegation warning: target {target_agent_id} has status {target_state.status}"
            )

        return DelegationResult.SUCCESS

    def try_delegate(
        self,
        source_agent_id: str,
        capability_needed: str,
        task_id: str,
        workflow_id: str,
        existing_chain: Optional[List[str]] = None,
        reason: str = "workload_distribution",
        handoff_snapshot_id: Optional[str] = None,
        target_agent_id: Optional[str] = None,
    ) -> DelegationResult:
        """
        Attempt to delegate a task, subject to policy constraints.

        If target_agent_id is not provided, uses capability registry
        to find and select an appropriate agent.

        Args:
            source_agent_id: Agent delegating the task
            capability_needed: Required capability for the task
            task_id: Task being delegated
            workflow_id: Workflow containing the task
            existing_chain: Optional prior delegation chain
            reason: Reason for delegation
            handoff_snapshot_id: Optional state snapshot for handoff
            target_agent_id: Optional specific target (auto-selected if None)

        Returns:
            DelegationResult indicating success or reason for failure
        """
        chain = list(existing_chain) if existing_chain else []

        if not chain and source_agent_id:
            chain = [source_agent_id] + existing_chain if existing_chain else [source_agent_id]

        if target_agent_id is None:
            candidates = self._capability_registry.find_agents_for_capability(
                capability_needed
            )

            available_candidates = []
            for c in candidates:
                check = self.can_delegate(
                    source_agent_id=source_agent_id,
                    target_agent_id=c.agent_id,
                    capability_needed=capability_needed,
                    existing_chain=chain,
                )
                if check == DelegationResult.SUCCESS:
                    available_candidates.append(c)

            if not available_candidates:
                if candidates:
                    logger.warning(
                        f"No available candidates after policy check. "
                        f"Found {len(candidates)} but none passed guardrails."
                    )
                    return DelegationResult.POLICY_DENIED
                logger.warning(f"No agents found with capability: {capability_needed}")
                return DelegationResult.NO_AGENT_AVAILABLE

            selected = self._capability_registry.select_agent(
                capability_needed, strategy=self._selection_strategy
            )
            if selected is None:
                return DelegationResult.NO_AGENT_AVAILABLE
            target_agent_id = selected.agent_id

        else:
            check_result = self.can_delegate(
                source_agent_id=source_agent_id,
                target_agent_id=target_agent_id,
                capability_needed=capability_needed,
                existing_chain=chain,
            )
            if check_result != DelegationResult.SUCCESS:
                return check_result

        source_state = self._state_store.get(source_agent_id)
        target_state = self._state_store.get(target_agent_id)

        source_role = source_state.role if source_state else "unknown"
        target_role = "unknown"

        target_reg = self._capability_registry.get_registration(target_agent_id)
        if target_reg:
            target_role = target_reg.role

        full_chain = chain + [target_agent_id]

        record = DelegationRecord(
            source_agent_id=source_agent_id,
            source_role=source_role,
            target_agent_id=target_agent_id,
            target_role=target_role,
            workflow_id=workflow_id,
            task_id=task_id,
            capability_needed=capability_needed,
            result=DelegationResult.SUCCESS,
            delegation_chain=list(chain),
            handoff_snapshot_id=handoff_snapshot_id,
            metadata={"reason": reason},
        )

        with self._lock:
            self._records[record.record_id] = record
            self._active_chains[task_id] = full_chain

        if source_state:
            source_state.status = AgentStatus.HANDING_OFF
            self._state_store.update(source_state)

        logger.info(
            f"Delegation recorded: {source_agent_id} -> {target_agent_id} "
            f"(task={task_id}, capability={capability_needed}, chain_depth={len(full_chain)})"
        )

        return DelegationResult.SUCCESS

    def get_chain_for_task(self, task_id: str) -> Optional[List[str]]:
        """Get the delegation chain for a task.

        Args:
            task_id: Task to look up

        Returns:
            List of agent IDs in delegation order, or None if not tracked
        """
        with self._lock:
            return self._active_chains.get(task_id)

    def get_record(self, record_id: str) -> Optional[DelegationRecord]:
        """Get a specific delegation record by ID.

        Args:
            record_id: Record ID to look up

        Returns:
            DelegationRecord or None if not found
        """
        with self._lock:
            return self._records.get(record_id)

    def get_all_records(self) -> List[DelegationRecord]:
        """Get all delegation records (for audit/debugging).

        Returns:
            List of all DelegationRecords
        """
        with self._lock:
            return list(self._records.values())

    def complete_delegation(
        self,
        task_id: str,
        outcome: str,
        error_message: Optional[str] = None,
    ) -> bool:
        """Mark a delegation chain as completed.

        Args:
            task_id: Task that was delegated
            outcome: Final outcome from DelegationOutcome
            error_message: Optional error description

        Returns:
            True if records were updated
        """
        with self._lock:
            updated = False
            for record in self._records.values():
                if record.task_id == task_id and record.completed_at is None:
                    record.mark_completed(outcome, error_message)
                    updated = True

            if task_id in self._active_chains and outcome in (
                DelegationOutcome.COMPLETED,
                DelegationOutcome.ROLLED_BACK,
            ):
                del self._active_chains[task_id]

            return updated

    def get_current_chain_depth(self, task_id: str) -> int:
        """Get the current chain depth for a task.

        Args:
            task_id: Task to check

        Returns:
            Current chain depth (0 = no delegation, 1 = 1 hop, etc.)
        """
        chain = self.get_chain_for_task(task_id)
        return len(chain) if chain else 0

    def can_accept_delegation(
        self,
        target_agent_id: str,
        source_agent_id: str,
        task_id: str,
        capability_needed: str,
    ) -> bool:
        """Check if an agent should accept a delegation from another agent.

        Used by the receiving agent to validate incoming delegation requests.

        Args:
            target_agent_id: Agent being asked to accept
            source_agent_id: Agent sending the delegation
            task_id: Task being delegated
            capability_needed: Capability required

        Returns:
            True if delegation should be accepted
        """
        target_reg = self._capability_registry.get_registration(target_agent_id)
        if target_reg and capability_needed not in target_reg.capabilities:
            logger.warning(
                f"Agent {target_agent_id} cannot accept: missing capability {capability_needed}"
            )
            return False

        target_state = self._state_store.get(target_agent_id)
        if target_state and target_state.status in (
            AgentStatus.RUNNING,
            AgentStatus.BLOCKED,
            AgentStatus.ERROR,
        ):
            if target_state.status == AgentStatus.RUNNING:
                logger.info(f"Agent {target_agent_id} is RUNNING but may still accept")
            else:
                logger.warning(
                    f"Agent {target_agent_id} has status {target_state.status}, may decline"
                )

        existing_chain = self.get_chain_for_task(task_id)
        if existing_chain and target_agent_id in existing_chain:
            logger.warning(
                f"Circular delegation detected: {target_agent_id} already in chain {existing_chain}"
            )
            return False

        return True

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about delegation activity.

        Returns:
            Dict with counts and metrics
        """
        with self._lock:
            total_records = len(self._records)
            active_chains = len(self._active_chains)

            outcomes: Dict[str, int] = {}
            results: Dict[str, int] = {}

            for record in self._records.values():
                if record.outcome:
                    outcomes[record.outcome] = outcomes.get(record.outcome, 0) + 1
                results[record.result] = results.get(record.result, 0) + 1

            max_depth = 0
            for chain in self._active_chains.values():
                max_depth = max(max_depth, len(chain))

            return {
                "total_delegations": total_records,
                "active_chains": active_chains,
                "max_active_chain_depth": max_depth,
                "outcomes": outcomes,
                "results": results,
                "policy": {
                    "allow_delegation": self.policy.allow_delegation,
                    "max_delegation_depth": self.policy.max_delegation_depth,
                    "require_capability_match": self.policy.require_capability_match,
                },
            }


_default_guardrails: Optional[DelegationGuardrails] = None


def default_guardrails() -> DelegationGuardrails:
    """Get the default global DelegationGuardrails instance."""
    global _default_guardrails
    if _default_guardrails is None:
        _default_guardrails = DelegationGuardrails()
    return _default_guardrails
