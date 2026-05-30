import pytest
from pathlib import Path
from cherenkov.core.agent_state_store import AgentStateStore, FileAgentStateBackend, AgentStatus
from cherenkov.core.c2_hub import C2Hub

@pytest.fixture
def temp_state_store(tmp_path):
    backend = FileAgentStateBackend(storage_dir=str(tmp_path / "agent_state"))
    return AgentStateStore(backend=backend)

@pytest.fixture
def c2_hub(tmp_path, temp_state_store):
    ssot_path = tmp_path / "context.md"
    ssot_path.write_text("# Test SSOT", encoding="utf-8")
    return C2Hub(ssot_path=str(ssot_path), state_store=temp_state_store)

def test_hub_ssot(c2_hub):
    assert "# Test SSOT" in c2_hub.get_ssot_content()
    c2_hub.update_ssot("# New SSOT", "agent-1")
    assert "# New SSOT" in c2_hub.get_ssot_content()

def test_assume_role(c2_hub, temp_state_store):
    temp_state_store.get_or_create("agent-1", "coordinator")
    assert c2_hub.assume_c2_role("agent-1") is True
    assert c2_hub.get_active_c2_agent().agent_id == "agent-1"

def test_handover_flow(c2_hub, temp_state_store):
    source = temp_state_store.get_or_create("source", "developer")
    target = temp_state_store.get_or_create("target", "tester")

    source.context["key"] = "value"
    temp_state_store.update(source)

    snapshot_id = c2_hub.initiate_handover("source", "target", "scaling")
    assert snapshot_id is not None

    assert temp_state_store.get("source").status == AgentStatus.HANDING_OFF
    assert temp_state_store.get("target").status == AgentStatus.RECEIVING_HANDOFF

    success = c2_hub.complete_handover(snapshot_id)
    assert success is True

    updated_target = temp_state_store.get("target")
    assert updated_target.status == AgentStatus.READY
    assert updated_target.context["key"] == "value"

    assert temp_state_store.get("source").status == AgentStatus.IDLE

def test_hub_status(c2_hub, temp_state_store):
    temp_state_store.get_or_create("agent-1", "coordinator")
    c2_hub.assume_c2_role("agent-1")

    status = c2_hub.get_hub_status()
    assert status["active_c2_agent"] == "agent-1"
    assert len(status["agents"]) >= 1
