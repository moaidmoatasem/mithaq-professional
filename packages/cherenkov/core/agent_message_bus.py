"""
Agent Message Bus - High-level messaging wrapper for agents.

Wraps the existing EventBus from events.py to provide:
- Agent-specific send/receive patterns
- Topic subscription convenience
- Message validation and serialization
- Request-response patterns with correlation IDs

This is the recommended way for agents to communicate, rather than
using EventBus directly.

Integration:
- Uses EventBus (pub/sub) as the underlying transport
- Uses AgentMessage for type-safe messages
- Uses topic helpers from agent_messages.py
"""

import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional

from cherenkov.core.agent_messages import (
    AgentMessage,
    MessagePriority,
    topic_for_agent,
    topic_for_capability,
    topic_for_role,
    topic_for_workflow,
)
from cherenkov.core.events import EventBus
from cherenkov.core.events import event_bus as global_event_bus

logger = logging.getLogger(__name__)


class PendingRequest:
    """Track a pending request waiting for response."""

    def __init__(
        self,
        request_id: str,
        timeout_seconds: float = 30.0,
    ):
        self.request_id = request_id
        self.timeout_seconds = timeout_seconds
        self.response: Optional[AgentMessage] = None
        self.error: Optional[str] = None
        self.event = asyncio.Event()
        self.created_at = asyncio.get_event_loop().time() if asyncio.get_event_loop() else None


class AgentMessageBus:
    """
    High-level message bus for agent-to-agent communication.

    Wraps EventBus with agent-specific patterns:
    - Direct messaging: send_to_agent(agent_id, message)
    - Role-based multicast: send_to_role(role, message)
    - Capability-based routing: send_to_capable(capability, message)
    - Workflow broadcast: send_to_workflow(workflow_id, message)
    - Request-response: request(agent_id, request) -> response

    Example:
        bus = AgentMessageBus(my_agent_id)

        # Subscribe to messages
        bus.on_message(handle_incoming_message)

        # Send direct message
        bus.send_to_agent("other-agent-id", AgentMessage(...))

        # Request-response (async)
        response = await bus.request("other-agent-id", request_msg)
    """

    def __init__(
        self,
        agent_id: str,
        event_bus: Optional[EventBus] = None,
    ):
        """Initialize AgentMessageBus for a specific agent.

        Args:
            agent_id: Unique ID of the agent using this bus
            event_bus: Optional EventBus to use (uses global if not provided)
        """
        self.agent_id = agent_id
        self._bus = event_bus or global_event_bus
        self._subscriptions: Dict[str, List[Callable[..., Any]]] = {}
        self._pending_requests: Dict[str, PendingRequest] = {}
        self._my_topic = topic_for_agent(agent_id)

        self._auto_subscribe()

    def _auto_subscribe(self) -> None:
        """Automatically subscribe to my personal topic."""
        self._bus.subscribe(self._my_topic, self._handle_event_bus_message)
        self._subscriptions[self._my_topic] = [self._handle_event_bus_message]

    def _handle_event_bus_message(self, **kwargs: Any) -> None:
        """Handle incoming message from EventBus.

        Extracts AgentMessage from kwargs and routes to subscribers.
        """
        message = kwargs.get("message")
        if message is None:
            logger.warning(f"Received event without 'message' kwarg: {kwargs.keys()}")
            return

        if isinstance(message, dict):
            try:
                message = AgentMessage.from_dict(message)
            except Exception as e:
                logger.error(f"Failed to deserialize message: {e}")
                return

        if isinstance(message, AgentMessage):
            if message.in_reply_to and message.in_reply_to in self._pending_requests:
                pending = self._pending_requests.pop(message.in_reply_to)
                pending.response = message
                if hasattr(pending.event, "set"):
                    try:
                        pending.event.set()
                    except Exception:
                        pass
                logger.debug(
                    f"Agent {self.agent_id} received response to request {message.in_reply_to}"
                )
                return

            for topic in self._subscriptions:
                for callback in self._subscriptions[topic]:
                    try:
                        callback(message)
                    except Exception as e:
                        logger.error(f"Error in message callback for agent {self.agent_id}: {e}")

    def subscribe(self, topic: str, callback: Callable[[AgentMessage], Any]) -> None:
        """Subscribe to messages on a specific topic.

        Args:
            topic: Topic to subscribe to (use topic_for_* helpers)
            callback: Function called when message arrives on topic
        """
        if topic not in self._subscriptions:
            self._subscriptions[topic] = []

        self._subscriptions[topic].append(callback)

        def bus_callback(**kwargs):
            message = kwargs.get("message")
            if isinstance(message, dict):
                message = AgentMessage.from_dict(message)
            if isinstance(message, AgentMessage):
                callback(message)

        self._bus.subscribe(topic, bus_callback)
        logger.debug(f"Agent {self.agent_id} subscribed to topic: {topic}")

    def subscribe_to_role(self, role: str, callback: Callable[[AgentMessage], Any]) -> None:
        """Subscribe to all messages for agents of a specific role.

        Args:
            role: Role to subscribe to (e.g., 'developer', 'security_analyst')
            callback: Message handler
        """
        self.subscribe(topic_for_role(role), callback)

    def subscribe_to_capability(
        self, capability: str, callback: Callable[[AgentMessage], Any]
    ) -> None:
        """Subscribe to all messages for agents with a specific capability.

        Args:
            capability: Capability to subscribe to
            callback: Message handler
        """
        self.subscribe(topic_for_capability(capability), callback)

    def subscribe_to_workflow(
        self, workflow_id: str, callback: Callable[[AgentMessage], Any]
    ) -> None:
        """Subscribe to all messages for a specific workflow.

        Args:
            workflow_id: Workflow to subscribe to
            callback: Message handler
        """
        self.subscribe(topic_for_workflow(workflow_id), callback)

    def on_message(self, callback: Callable[[AgentMessage], Any]) -> None:
        """Register a callback for direct messages to this agent.

        Convenience method for the most common use case.

        Args:
            callback: Function called when messages arrive for this agent
        """
        if self._my_topic not in self._subscriptions:
            self._subscriptions[self._my_topic] = []
        else:
            self._subscriptions[self._my_topic] = [
                cb
                for cb in self._subscriptions[self._my_topic]
                if cb != self._handle_event_bus_message
            ]

        def wrapper(message: AgentMessage) -> Any:
            return callback(message)

        self._subscriptions[self._my_topic].append(wrapper)
        self._subscriptions[self._my_topic].append(self._handle_event_bus_message)

    def publish(self, topic: str, message: AgentMessage) -> None:
        """Publish a message to a specific topic.

        Args:
            topic: Topic to publish on
            message: Message to publish
        """
        if not isinstance(message, AgentMessage):
            raise TypeError(f"Expected AgentMessage, got {type(message)}")

        self._bus.publish(topic, message=message.to_dict())
        logger.debug(
            f"Agent {self.agent_id} published to {topic}: "
            f"type={message.message_type}, id={message.message_id}"
        )

    def send_to_agent(self, target_agent_id: str, message: AgentMessage) -> None:
        """Send a direct message to a specific agent.

        Args:
            target_agent_id: ID of agent to receive message
            message: Message to send
        """
        message.target_agent_id = target_agent_id
        self.publish(topic_for_agent(target_agent_id), message)

    def send_to_role(self, role: str, message: AgentMessage) -> None:
        """Send a message to all agents of a specific role.

        Args:
            role: Role name (e.g., 'developer', 'security_analyst')
            message: Message to send
        """
        self.publish(topic_for_role(role), message)

    def send_to_capable(self, capability: str, message: AgentMessage) -> None:
        """Send a message to all agents with a specific capability.

        Args:
            capability: Required capability
            message: Message to send
        """
        self.publish(topic_for_capability(capability), message)

    def send_to_workflow(self, workflow_id: str, message: AgentMessage) -> None:
        """Send a message to all participants in a workflow.

        Args:
            workflow_id: Workflow ID
            message: Message to send
        """
        message.workflow_id = workflow_id
        self.publish(topic_for_workflow(workflow_id), message)

    def create_message(
        self,
        message_type: str,
        payload: Dict[str, Any],
        priority: int = MessagePriority.NORMAL,
    ) -> AgentMessage:
        """Create a message pre-configured with this agent as source.

        Args:
            message_type: Type from MessageType enum
            payload: Message content
            priority: Priority level

        Returns:
            New AgentMessage with source_agent_id set
        """
        return AgentMessage(
            message_type=message_type,
            source_agent_id=self.agent_id,
            payload=payload,
            priority=priority,
        )

    def send_task_request(
        self,
        target_agent_id: str,
        task_description: str,
        task_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        requirements: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentMessage:
        """Create and send a standardized task request.

        Convenience method for sending task_request messages.

        Args:
            target_agent_id: Agent to receive the task
            task_description: What needs to be done
            task_id: Optional existing task ID
            workflow_id: Optional workflow context
            requirements: Optional dict of requirements
            context: Optional context data

        Returns:
            The message that was sent
        """
        from cherenkov.core.agent_messages import create_task_request

        message = create_task_request(
            source_agent_id=self.agent_id,
            target_agent_id=target_agent_id,
            task_description=task_description,
            task_id=task_id,
            workflow_id=workflow_id,
            requirements=requirements,
            context=context,
        )

        self.send_to_agent(target_agent_id, message)
        return message

    def send_delegation_request(
        self,
        target_agent_id: str,
        task_id: str,
        workflow_id: str,
        handoff_snapshot_id: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> AgentMessage:
        """Create and send a delegation request.

        Args:
            target_agent_id: Agent being asked to take over
            task_id: Task being delegated
            workflow_id: Workflow containing the task
            handoff_snapshot_id: Optional state snapshot ID
            reason: Optional reason for delegation

        Returns:
            The message that was sent
        """
        from cherenkov.core.agent_messages import create_delegation_request

        message = create_delegation_request(
            source_agent_id=self.agent_id,
            target_agent_id=target_agent_id,
            task_id=task_id,
            workflow_id=workflow_id,
            handoff_snapshot_id=handoff_snapshot_id,
            reason=reason,
        )

        self.send_to_agent(target_agent_id, message)
        return message

    def reply_to(
        self,
        original_message: AgentMessage,
        message_type: str,
        payload: Dict[str, Any],
    ) -> AgentMessage:
        """Create a reply to a received message.

        Sets in_reply_to and target_agent_id appropriately.

        Args:
            original_message: Message being replied to
            message_type: Type of reply
            payload: Reply content

        Returns:
            New reply message (already sent)
        """
        reply = original_message.create_reply(
            message_type=message_type,
            payload=payload,
            source_agent_id=self.agent_id,
        )

        if original_message.source_agent_id:
            self.send_to_agent(original_message.source_agent_id, reply)

        return reply

    def unsubscribe(self, topic: str) -> None:
        """Unsubscribe from a topic (internal only, callback tracking limited)."""
        if topic in self._subscriptions:
            del self._subscriptions[topic]
        logger.debug(f"Agent {self.agent_id} unsubscribed from topic: {topic}")

    def get_stats(self) -> Dict[str, Any]:
        """Get messaging statistics.

        Returns:
            Dict with subscription and pending request info
        """
        return {
            "agent_id": self.agent_id,
            "subscribed_topics": list(self._subscriptions.keys()),
            "pending_requests": len(self._pending_requests),
        }


_default_buses: Dict[str, AgentMessageBus] = {}


def get_message_bus_for_agent(agent_id: str) -> AgentMessageBus:
    """Get or create a cached AgentMessageBus for an agent.

    Args:
        agent_id: Agent ID

    Returns:
        Cached or new AgentMessageBus
    """
    global _default_buses
    if agent_id not in _default_buses:
        _default_buses[agent_id] = AgentMessageBus(agent_id)
    return _default_buses[agent_id]
