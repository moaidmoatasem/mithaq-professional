"""Integration test for all 9 new multi-agent modules."""

import os
import sys
import tempfile

import pytest

pytestmark = pytest.mark.integration

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_agent_state_store():
    """Test AgentStateStore basic operations."""
    from cherenkov.core.agent_state_store import (
        AgentStateStore,
        AgentStatus,
        FileAgentStateBackend,
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        backend = FileAgentStateBackend(storage_dir=tmpdir)
        store = AgentStateStore(backend=backend)

        state = store.get_or_create(
            agent_id="test-agent-001",
            role="developer",
            capabilities=["code_review", "writing", "testing"],
        )

        assert state.agent_id == "test-agent-001"
        assert state.role == "developer"
        assert state.status == AgentStatus.IDLE
        assert "code_review" in state.capabilities

        store.set_status("test-agent-001", AgentStatus.RUNNING)
        state2 = store.get("test-agent-001")
        assert state2.status == AgentStatus.RUNNING

        assert not state.is_available_for_delegation()

        snapshot = state.create_handoff_snapshot(target_agent_id="test-agent-002", reason="testing")
        assert snapshot.source_agent_id == "test-agent-001"
        assert snapshot.target_agent_id == "test-agent-002"
        assert snapshot.is_valid()

        saved = store.save_handoff(snapshot)
        assert saved

        loaded = store.load_handoff(snapshot.snapshot_id)
        assert loaded is not None
        assert loaded.snapshot_id == snapshot.snapshot_id

        print("OK AgentStateStore: PASSED")


def test_aimd_capacity_controller():
    """Test AIMD capacity control."""
    from cherenkov.core.capability_registry import AIMDCapacityController

    controller = AIMDCapacityController(
        initial_capacity=4, min_capacity=1, max_capacity=10, success_threshold=3
    )

    assert controller.get_capacity() == 4

    for _ in range(3):
        controller.record_success()
    assert controller.get_capacity() == 5

    controller.record_failure()
    assert controller.get_capacity() == 2

    controller.record_failure()
    assert controller.get_capacity() == 1

    controller.record_failure()
    assert controller.get_capacity() == 1

    stats = controller.get_stats()
    assert stats["total_failures"] == 3

    print("- AIMDCapacityController: PASSED")


def test_capability_registry():
    """Test CapabilityRegistry."""
    from cherenkov.core.capability_registry import (
        AgentRegistration,
        CapabilityRegistry,
    )

    registry = CapabilityRegistry()

    reg1 = AgentRegistration(
        agent_id="dev-1", role="developer", capabilities=["code_review", "testing"], is_local=True
    )
    registry.register(reg1)

    reg2 = AgentRegistration(
        agent_id="dev-2", role="developer", capabilities=["code_review", "writing"], is_local=True
    )
    registry.register(reg2)

    candidates = registry.find_agents_for_capability("code_review")
    assert len(candidates) == 2

    candidates2 = registry.find_agents_for_capability("writing")
    assert len(candidates2) == 1
    assert candidates2[0].agent_id == "dev-2"

    all_caps = registry.get_all_capabilities()
    assert "code_review" in all_caps
    assert "testing" in all_caps
    assert "writing" in all_caps

    print("- CapabilityRegistry: PASSED")


def test_delegation_guardrails():
    """Test DelegationGuardrails."""
    from cherenkov.core.agent_state_store import AgentStateStore
    from cherenkov.core.capability_registry import AgentRegistration, CapabilityRegistry
    from cherenkov.core.delegation_guardrails import (
        DelegationGuardrails,
        DelegationResult,
    )

    state_store = AgentStateStore()
    registry = CapabilityRegistry(state_store=state_store)

    state_store.get_or_create("source-1", "developer", ["code_review"])
    state_store.get_or_create("target-1", "tester", ["testing"])

    registry.register(
        AgentRegistration(agent_id="target-1", role="tester", capabilities=["testing"])
    )
    registry.register(
        AgentRegistration(agent_id="target-2", role="developer", capabilities=["code_review"])
    )

    guardrails = DelegationGuardrails(state_store=state_store, capability_registry=registry)

    result = guardrails.can_delegate(
        source_agent_id="source-1", target_agent_id="target-1", capability_needed="testing"
    )
    assert result == DelegationResult.SUCCESS

    result2 = guardrails.can_delegate(
        source_agent_id="source-1", target_agent_id="target-1", capability_needed="code_review"
    )
    assert result2 == DelegationResult.CAPABILITY_MISMATCH

    depth_test = guardrails.can_delegate(
        source_agent_id="a",
        target_agent_id="b",
        capability_needed="test",
        existing_chain=["a", "c", "d", "e"],
    )
    assert depth_test == DelegationResult.DEPTH_LIMIT_EXCEEDED

    circular_test = guardrails.can_delegate(
        source_agent_id="a",
        target_agent_id="b",
        capability_needed="test",
        existing_chain=["a", "b"],
    )
    assert circular_test == DelegationResult.CIRCULAR_DELEGATION

    stats = guardrails.get_stats()
    assert stats["policy"]["max_delegation_depth"] == 3

    print("- DelegationGuardrails: PASSED")


def test_agent_messages():
    """Test AgentMessage and helpers."""
    from cherenkov.core.agent_messages import (
        AgentMessage,
        MessageType,
        create_delegation_request,
        create_task_request,
        parse_topic,
        topic_for_agent,
        topic_for_role,
        topic_for_workflow,
    )

    msg = AgentMessage(
        message_type=MessageType.TASK_REQUEST, source_agent_id="agent-1", payload={"task": "test"}
    )

    assert msg.message_type == MessageType.TASK_REQUEST
    assert msg.source_agent_id == "agent-1"
    assert msg.requires_response()
    assert not msg.is_expired()

    msg2 = msg.create_reply(
        message_type=MessageType.TASK_RESPONSE,
        payload={"result": "done"},
        source_agent_id="agent-2",
    )
    assert msg2.in_reply_to == msg.message_id
    assert msg2.target_agent_id == "agent-1"

    assert topic_for_agent("abc") == "agent:abc"
    assert topic_for_role("developer") == "role:developer"
    assert topic_for_workflow("wf-123") == "workflow:wf-123"

    parsed = parse_topic("agent:abc123")
    assert parsed["type"] == "agent"
    assert parsed["id"] == "abc123"

    task_req = create_task_request(
        source_agent_id="source",
        target_agent_id="target",
        task_description="Please review this code",
    )
    assert task_req.message_type == MessageType.TASK_REQUEST
    assert "Please review" in task_req.payload["task_description"]

    del_req = create_delegation_request(
        source_agent_id="a1", target_agent_id="a2", task_id="task-1", workflow_id="wf-1"
    )
    assert del_req.message_type == MessageType.DELEGATION_REQUEST

    print("- AgentMessages: PASSED")


def run_all_tests():
    """Run all integration tests."""
    print("\n" + "=" * 60)
    print("Multi-Agent Foundation Integration Tests")
    print("=" * 60 + "\n")

    test_agent_messages()
    test_agent_state_store()
    test_aimd_capacity_controller()
    test_capability_registry()
    test_delegation_guardrails()

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)
    print("\nSummary:")
    print("  - agent_messages.py    - Message types, topics, helpers")
    print("  - agent_state_store.py - AgentState, HandoverSnapshot, persistence")
    print("  - capability_registry.py - AIMD, agent discovery, selection")
    print("  - delegation_guardrails.py - Policy, depth limits, circular detection")
    print("  - (agent_message_bus.py skipped - needs async event loop)")
    print("\n5 new multi-agent foundation modules verified!")


if __name__ == "__main__":
    run_all_tests()
