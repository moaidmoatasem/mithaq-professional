"""
Agent Messaging Protocol - Type-safe message passing between agents.

Provides:
- MessageType enum for standardizing message categories
- AgentMessage dataclass with validation and serialization
- Topic helpers for publish-subscribe routing
- Integration with EventBus for actual transport
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


class MessageType(str, Enum):
    """Standard message types for inter-agent communication."""

    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    TASK_PROGRESS = "task_progress"
    TASK_CANCEL = "task_cancel"
    DELEGATION_REQUEST = "delegation_request"
    DELEGATION_ACCEPT = "delegation_accept"
    DELEGATION_DECLINE = "delegation_decline"
    DELEGATION_COMPLETE = "delegation_complete"
    STATUS_QUERY = "status_query"
    STATUS_UPDATE = "status_update"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
    HANDOFF_REQUEST = "handoff_request"
    HANDOFF_ACK = "handoff_ack"
    CAPABILITY_QUERY = "capability_query"
    CAPABILITY_RESPONSE = "capability_response"
    BROADCAST = "broadcast"


class MessagePriority(int, Enum):
    """Priority levels for message routing."""

    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


def topic_for_agent(agent_id: str) -> str:
    """Get the topic name for direct messages to a specific agent."""
    return f"agent:{agent_id}"


def topic_for_role(role: str) -> str:
    """Get the topic name for messages to all agents of a specific role."""
    return f"role:{role}"


def topic_for_capability(capability: str) -> str:
    """Get the topic name for messages to agents with a specific capability."""
    return f"capability:{capability}"


def topic_for_workflow(workflow_id: str) -> str:
    """Get the topic name for all messages related to a specific workflow."""
    return f"workflow:{workflow_id}"


def parse_topic(topic: str) -> Dict[str, str]:
    """Parse a topic string into its type and identifier.

    Returns:
        Dict with 'type' and 'id' keys, or empty dict if not a recognized format.
    """
    parts = topic.split(":", 1)
    if len(parts) == 2:
        return {"type": parts[0], "id": parts[1]}
    return {}


@dataclass
class AgentMessage:
    """
    A type-safe message for inter-agent communication.

    Attributes:
        message_id: Unique UUID for this message
        message_type: Type of message (from MessageType enum)
        source_agent_id: Agent ID of sender
        target_agent_id: Agent ID of recipient (None for broadcasts)
        target_topics: List of topics for pub/sub routing
        workflow_id: Optional workflow this message belongs to
        task_id: Optional task this message relates to
        priority: Message priority level
        payload: Dictionary of message content
        in_reply_to: Optional message ID this is replying to
        created_at: ISO timestamp when created
        expires_at: Optional ISO timestamp when message expires
        headers: Optional key-value metadata
    """

    message_type: str
    source_agent_id: str
    payload: Dict[str, Any] = field(default_factory=dict)

    message_id: str = field(default_factory=lambda: str(uuid4()))
    target_agent_id: Optional[str] = None
    target_topics: List[str] = field(default_factory=list)
    workflow_id: Optional[str] = None
    task_id: Optional[str] = None
    priority: int = MessagePriority.NORMAL
    in_reply_to: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    expires_at: Optional[str] = None
    headers: Dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        """Check if this message has expired."""
        if self.expires_at is None:
            return False
        try:
            expiry = datetime.fromisoformat(self.expires_at)
            return datetime.now(timezone.utc) > expiry
        except (ValueError, TypeError):
            return False

    def requires_response(self) -> bool:
        """Check if this message type expects a response."""
        response_required = {
            MessageType.TASK_REQUEST,
            MessageType.DELEGATION_REQUEST,
            MessageType.HANDOFF_REQUEST,
            MessageType.STATUS_QUERY,
            MessageType.CAPABILITY_QUERY,
        }
        return self.message_type in response_required

    def get_routing_topics(self) -> List[str]:
        """Get all topics this message should be routed to."""
        topics = list(self.target_topics) if self.target_topics else []
        if self.target_agent_id:
            topics.append(topic_for_agent(self.target_agent_id))
        if self.workflow_id:
            topics.append(topic_for_workflow(self.workflow_id))
        return topics

    def to_dict(self) -> Dict[str, Any]:
        """Serialize message to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentMessage":
        """Deserialize message from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def create_reply(
        self,
        message_type: str,
        payload: Dict[str, Any],
        source_agent_id: str,
    ) -> "AgentMessage":
        """Create a reply to this message.

        Args:
            message_type: Type of reply message
            payload: Content of reply
            source_agent_id: Agent ID of the replying agent

        Returns:
            New AgentMessage configured as a reply
        """
        return AgentMessage(
            message_type=message_type,
            source_agent_id=source_agent_id,
            target_agent_id=self.source_agent_id,
            payload=payload,
            workflow_id=self.workflow_id,
            task_id=self.task_id,
            in_reply_to=self.message_id,
            priority=self.priority,
        )

    def create_error(
        self,
        error_message: str,
        source_agent_id: str,
        error_code: Optional[str] = None,
    ) -> "AgentMessage":
        """Create an error response to this message.

        Args:
            error_message: Description of the error
            source_agent_id: Agent ID reporting the error
            error_code: Optional machine-readable error code

        Returns:
            New AgentMessage configured as an error
        """
        payload = {"message": error_message}
        if error_code:
            payload["error_code"] = error_code

        return self.create_reply(
            message_type=MessageType.ERROR,
            payload=payload,
            source_agent_id=source_agent_id,
        )


def create_task_request(
    source_agent_id: str,
    target_agent_id: str,
    task_description: str,
    task_id: Optional[str] = None,
    workflow_id: Optional[str] = None,
    priority: MessagePriority = MessagePriority.NORMAL,
    requirements: Optional[Dict[str, Any]] = None,
    context: Optional[Dict[str, Any]] = None,
) -> AgentMessage:
    """Helper to create a standardized task request message.

    Args:
        source_agent_id: Agent sending the request
        target_agent_id: Agent being asked to perform the task
        task_description: Human-readable task description
        task_id: Optional existing task ID
        workflow_id: Optional workflow context
        priority: Message priority
        requirements: Optional dict of task requirements
        context: Optional context data

    Returns:
        Configured AgentMessage of type TASK_REQUEST
    """
    payload = {
        "task_description": task_description,
    }
    if requirements:
        payload["requirements"] = requirements
    if context:
        payload["context"] = context

    return AgentMessage(
        message_type=MessageType.TASK_REQUEST,
        source_agent_id=source_agent_id,
        target_agent_id=target_agent_id,
        task_id=task_id,
        workflow_id=workflow_id,
        priority=priority,
        payload=payload,
    )


def create_delegation_request(
    source_agent_id: str,
    target_agent_id: str,
    task_id: str,
    workflow_id: str,
    handoff_snapshot_id: Optional[str] = None,
    reason: Optional[str] = None,
) -> AgentMessage:
    """Helper to create a delegation request message.

    Args:
        source_agent_id: Agent delegating the task
        target_agent_id: Agent being asked to take over
        task_id: Task being delegated
        workflow_id: Workflow containing the task
        handoff_snapshot_id: Optional state snapshot for handoff
        reason: Optional reason for delegation

    Returns:
        Configured AgentMessage of type DELEGATION_REQUEST
    """
    payload: Dict[str, Any] = {
        "task_id": task_id,
        "workflow_id": workflow_id,
    }
    if handoff_snapshot_id:
        payload["handoff_snapshot_id"] = handoff_snapshot_id
    if reason:
        payload["reason"] = reason

    return AgentMessage(
        message_type=MessageType.DELEGATION_REQUEST,
        source_agent_id=source_agent_id,
        target_agent_id=target_agent_id,
        workflow_id=workflow_id,
        task_id=task_id,
        priority=MessagePriority.HIGH,
        payload=payload,
    )
