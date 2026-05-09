"""
Workflow Checkpoint Manager - Save and resume workflows from checkpoints.

Provides:
- Checkpoint creation at task boundaries
- Checkpoint storage (file-based, extensible)
- Workflow resumption from last checkpoint
- Partial rollback support
- Integration with AgentStateStore for agent state handover
"""

import json
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4


class CheckpointType(str, Enum):
    """Type of checkpoint."""

    TASK_COMPLETE = "task_complete"
    TASK_FAILED = "task_failed"
    WORKFLOW_START = "workflow_start"
    WORKFLOW_PAUSE = "workflow_pause"
    MANUAL = "manual"
    AGENT_HANDOFF = "agent_handoff"


class CheckpointStatus(str, Enum):
    """Status of a checkpoint."""

    ACTIVE = "active"
    SUPERSEDED = "superseded"
    ROLLED_BACK = "rolled_back"
    EXPIRED = "expired"


@dataclass
class TaskCheckpoint:
    """
    Checkpoint data for a single task in a workflow.

    Contains everything needed to resume or rollback a task:
    - Task configuration
    - Partial results
    - Agent state references
    - Next steps
    """

    task_index: int
    task_name: str
    task_config: Dict[str, Any]
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    agent_id: Optional[str] = None
    agent_role: Optional[str] = None
    state_snapshot_id: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    next_task_index: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskCheckpoint":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class WorkflowCheckpoint:
    """
    Complete checkpoint for a workflow execution.

    Can be used to:
    - Resume a failed workflow from last completed task
    - Rollback to a previous known-good state
    - Hand off workflow to another agent
    """

    checkpoint_id: str
    workflow_id: str
    workflow_name: str
    checkpoint_type: CheckpointType
    status: CheckpointStatus
    created_at: str
    created_by_agent_id: Optional[str] = None

    config: Dict[str, Any] = field(default_factory=dict)

    task_checkpoints: List[TaskCheckpoint] = field(default_factory=list)

    current_task_index: int = 0
    total_tasks: int = 0

    accumulated_results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    state_snapshot_id: Optional[str] = None

    previous_checkpoint_id: Optional[str] = None
    next_checkpoint_id: Optional[str] = None

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["checkpoint_type"] = self.checkpoint_type.value
        data["status"] = self.status.value
        data["task_checkpoints"] = [tc.to_dict() for tc in self.task_checkpoints]
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowCheckpoint":
        task_checkpoints_data = data.pop("task_checkpoints", [])
        task_checkpoints = [TaskCheckpoint.from_dict(tc) for tc in task_checkpoints_data]

        if "checkpoint_type" in data and isinstance(data["checkpoint_type"], str):
            data["checkpoint_type"] = CheckpointType(data["checkpoint_type"])
        if "status" in data and isinstance(data["status"], str):
            data["status"] = CheckpointStatus(data["status"])

        return cls(
            **{k: v for k, v in data.items() if k in cls.__dataclass_fields__},
            task_checkpoints=task_checkpoints,
        )

    def get_last_completed_task(self) -> Optional[TaskCheckpoint]:
        """Get the last successfully completed task checkpoint."""
        completed = [
            tc for tc in self.task_checkpoints
            if tc.status == "completed"
        ]
        if completed:
            return completed[-1]
        return None

    def get_next_task_to_execute(self) -> int:
        """Get the index of the next task to execute."""
        last = self.get_last_completed_task()
        if last is not None:
            return last.task_index + 1
        return 0

    def can_resume(self) -> bool:
        """Check if this checkpoint can be resumed."""
        return self.status == CheckpointStatus.ACTIVE

    def add_task_checkpoint(
        self,
        task_index: int,
        task_name: str,
        task_config: Dict[str, Any],
        status: str,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        agent_id: Optional[str] = None,
        state_snapshot_id: Optional[str] = None,
    ) -> TaskCheckpoint:
        """Add a task checkpoint to this workflow checkpoint."""
        tc = TaskCheckpoint(
            task_index=task_index,
            task_name=task_name,
            task_config=task_config,
            status=status,
            result=result,
            error=error,
            agent_id=agent_id,
            state_snapshot_id=state_snapshot_id,
            started_at=self.task_checkpoints[-1].completed_at if self.task_checkpoints else None,
            completed_at=datetime.now(timezone.utc).isoformat() if status == "completed" else None,
        )
        self.task_checkpoints.append(tc)

        if status == "completed" and result:
            self.accumulated_results[f"task_{task_index}"] = result

        if error:
            self.errors.append(error)

        return tc


class CheckpointBackend(ABC):
    """Abstract base for checkpoint storage backends."""

    @abstractmethod
    def save(self, checkpoint: WorkflowCheckpoint) -> str:
        pass

    @abstractmethod
    def load(self, checkpoint_id: str) -> Optional[WorkflowCheckpoint]:
        pass

    @abstractmethod
    def list_for_workflow(self, workflow_id: str) -> List[str]:
        pass

    @abstractmethod
    def get_latest_for_workflow(self, workflow_id: str) -> Optional[WorkflowCheckpoint]:
        pass

    @abstractmethod
    def update_status(self, checkpoint_id: str, status: CheckpointStatus) -> bool:
        pass


class FileCheckpointBackend(CheckpointBackend):
    """
    File-based JSON storage for workflow checkpoints.

    Directory structure:
        workflow_checkpoints/
            {workflow_id}/
                {checkpoint_id}.json    # Individual checkpoints
                latest.json              # Symlink/pointer to latest
    """

    def __init__(self, storage_dir: str = "workflow_checkpoints"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _get_workflow_dir(self, workflow_id: str) -> Path:
        workflow_dir = self.storage_dir / workflow_id
        workflow_dir.mkdir(parents=True, exist_ok=True)
        return workflow_dir

    def save(self, checkpoint: WorkflowCheckpoint) -> str:
        """Save a workflow checkpoint to JSON file."""
        workflow_dir = self._get_workflow_dir(checkpoint.workflow_id)
        filepath = workflow_dir / f"{checkpoint.checkpoint_id}.json"

        with open(filepath, "w") as f:
            json.dump(checkpoint.to_dict(), f, indent=2)

        latest_path = workflow_dir / "latest.json"
        with open(latest_path, "w") as f:
            json.dump({"checkpoint_id": checkpoint.checkpoint_id, "saved_at": checkpoint.created_at}, f, indent=2)

        return str(filepath)

    def load(self, checkpoint_id: str) -> Optional[WorkflowCheckpoint]:
        """Load a checkpoint by ID."""
        for workflow_dir in self.storage_dir.iterdir():
            if workflow_dir.is_dir():
                filepath = workflow_dir / f"{checkpoint_id}.json"
                if filepath.exists():
                    with open(filepath, "r") as f:
                        data = json.load(f)
                    return WorkflowCheckpoint.from_dict(data)
        return None

    def list_for_workflow(self, workflow_id: str) -> List[str]:
        """List all checkpoint IDs for a workflow."""
        workflow_dir = self._get_workflow_dir(workflow_id)
        checkpoints = []
        for filepath in workflow_dir.glob("*.json"):
            if filepath.stem not in ("latest",):
                checkpoints.append(filepath.stem)
        return checkpoints

    def get_latest_for_workflow(self, workflow_id: str) -> Optional[WorkflowCheckpoint]:
        """Get the most recent checkpoint for a workflow."""
        workflow_dir = self._get_workflow_dir(workflow_id)
        latest_path = workflow_dir / "latest.json"

        if not latest_path.exists():
            return None

        with open(latest_path, "r") as f:
            latest_data = json.load(f)

        checkpoint_id = latest_data.get("checkpoint_id")
        if checkpoint_id:
            return self.load(checkpoint_id)

        return None

    def update_status(self, checkpoint_id: str, status: CheckpointStatus) -> bool:
        """Update the status of a checkpoint."""
        checkpoint = self.load(checkpoint_id)
        if checkpoint is None:
            return False

        checkpoint.status = status
        self.save(checkpoint)
        return True


class WorkflowCheckpointManager:
    """
    Manager for workflow checkpoints.

    High-level interface for:
    - Creating checkpoints
    - Loading checkpoints
    - Resuming workflows from checkpoints
    - Rolling back to previous checkpoints
    """

    def __init__(
        self,
        backend: Optional[CheckpointBackend] = None,
        storage_dir: str = "workflow_checkpoints",
    ):
        self.backend = backend or FileCheckpointBackend(storage_dir)

    def create_checkpoint(
        self,
        workflow_id: str,
        workflow_name: str,
        checkpoint_type: CheckpointType,
        config: Dict[str, Any],
        task_checkpoints: Optional[List[TaskCheckpoint]] = None,
        current_task_index: int = 0,
        accumulated_results: Optional[Dict[str, Any]] = None,
        created_by_agent_id: Optional[str] = None,
        state_snapshot_id: Optional[str] = None,
        previous_checkpoint_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> WorkflowCheckpoint:
        """
        Create a new workflow checkpoint.

        Args:
            workflow_id: Unique workflow execution ID
            workflow_name: Workflow name/type
            checkpoint_type: Type of checkpoint
            config: Full workflow configuration
            task_checkpoints: List of task-level checkpoints
            current_task_index: Current task being executed
            accumulated_results: Results from completed tasks
            created_by_agent_id: Agent that created this checkpoint
            state_snapshot_id: Reference to AgentStateStore snapshot
            previous_checkpoint_id: Link to previous checkpoint for rollback
            metadata: Additional metadata

        Returns:
            The created WorkflowCheckpoint
        """
        now = datetime.now(timezone.utc).isoformat()
        total_tasks = len(config.get("tasks", []))

        checkpoint = WorkflowCheckpoint(
            checkpoint_id=str(uuid4()),
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            checkpoint_type=checkpoint_type,
            status=CheckpointStatus.ACTIVE,
            created_at=now,
            created_by_agent_id=created_by_agent_id,
            config=config,
            task_checkpoints=task_checkpoints or [],
            current_task_index=current_task_index,
            total_tasks=total_tasks,
            accumulated_results=accumulated_results or {},
            state_snapshot_id=state_snapshot_id,
            previous_checkpoint_id=previous_checkpoint_id,
            metadata=metadata or {},
        )

        self.backend.save(checkpoint)
        return checkpoint

    def get_checkpoint(self, checkpoint_id: str) -> Optional[WorkflowCheckpoint]:
        """Load a checkpoint by ID."""
        return self.backend.load(checkpoint_id)

    def get_latest_checkpoint(self, workflow_id: str) -> Optional[WorkflowCheckpoint]:
        """Get the most recent checkpoint for a workflow."""
        return self.backend.get_latest_for_workflow(workflow_id)

    def list_checkpoints(self, workflow_id: str) -> List[str]:
        """List all checkpoint IDs for a workflow."""
        return self.backend.list_for_workflow(workflow_id)

    def can_resume(self, workflow_id: str) -> bool:
        """Check if a workflow has a resumable checkpoint."""
        checkpoint = self.get_latest_checkpoint(workflow_id)
        if checkpoint is None:
            return False
        return checkpoint.can_resume()

    def get_resumption_point(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information needed to resume a workflow.

        Returns:
            Dict with: checkpoint_id, next_task_index, config, accumulated_results
            or None if no resumable checkpoint
        """
        checkpoint = self.get_latest_checkpoint(workflow_id)
        if checkpoint is None or not checkpoint.can_resume():
            return None

        next_task = checkpoint.get_next_task_to_execute()

        return {
            "checkpoint_id": checkpoint.checkpoint_id,
            "workflow_id": checkpoint.workflow_id,
            "workflow_name": checkpoint.workflow_name,
            "next_task_index": next_task,
            "total_tasks": checkpoint.total_tasks,
            "config": checkpoint.config,
            "accumulated_results": dict(checkpoint.accumulated_results),
            "task_checkpoints": [tc.to_dict() for tc in checkpoint.task_checkpoints],
            "state_snapshot_id": checkpoint.state_snapshot_id,
        }

    def mark_superseded(self, checkpoint_id: str) -> bool:
        """Mark a checkpoint as superseded (replaced by newer one)."""
        return self.backend.update_status(checkpoint_id, CheckpointStatus.SUPERSEDED)

    def mark_rolled_back(self, checkpoint_id: str) -> bool:
        """Mark a checkpoint as rolled back."""
        return self.backend.update_status(checkpoint_id, CheckpointStatus.ROLLED_BACK)


default_checkpoint_manager = WorkflowCheckpointManager()
