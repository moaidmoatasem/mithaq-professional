"""Tests for AgentRegistry class."""

import json
from pathlib import Path
from unittest.mock import Mock

from cherenkov.orchestration.agent_registry import AgentRegistry
from cherenkov.orchestration.types import AgentID


def test_register_with_role(tmp_path: Path):
    path = tmp_path / "registry.json"
    registry = AgentRegistry(path=path)
    mock_agent = Mock(role="researcher")

    agent_id = registry.register(mock_agent)

    assert isinstance(agent_id, AgentID)
    assert agent_id.role == "researcher"
    assert len(agent_id.id) > 0
    assert registry.count() == 1


def test_register_without_role_defaults_to_unknown(tmp_path: Path):
    path = tmp_path / "registry.json"
    registry = AgentRegistry(path=path)
    mock_agent = Mock(spec=[])  # no role attribute

    agent_id = registry.register(mock_agent)

    assert agent_id.role == "unknown"


def test_get_returns_registered_agent(tmp_path: Path):
    path = tmp_path / "registry.json"
    registry = AgentRegistry(path=path)
    mock_agent = Mock(role="tester")
    agent_id = registry.register(mock_agent)

    data = registry.get(agent_id.id)

    assert data is not None
    assert data["role"] == "tester"
    assert "registered_at" in data


def test_get_returns_none_for_missing_agent(tmp_path: Path):
    registry = AgentRegistry(path=tmp_path / "registry.json")

    result = registry.get("nonexistent-id")

    assert result is None


def test_list_all_returns_all_agents(tmp_path: Path):
    path = tmp_path / "registry.json"
    registry = AgentRegistry(path=path)
    registry.register(Mock(role="dev"))
    registry.register(Mock(role="ops"))

    all_agents = registry.list_all()

    assert len(all_agents) == 2
    roles = [a["role"] for a in all_agents.values()]
    assert "dev" in roles
    assert "ops" in roles


def test_count_returns_zero_for_empty_registry(tmp_path: Path):
    registry = AgentRegistry(path=tmp_path / "registry.json")

    assert registry.count() == 0


def test_count_after_multiple_registrations(tmp_path: Path):
    path = tmp_path / "registry.json"
    registry = AgentRegistry(path=path)
    registry.register(Mock(role="a"))
    registry.register(Mock(role="b"))
    registry.register(Mock(role="c"))

    assert registry.count() == 3


def test_persists_across_instances(tmp_path: Path):
    path = tmp_path / "registry.json"
    registry1 = AgentRegistry(path=path)
    agent_id = registry1.register(Mock(role="persistent"))

    registry2 = AgentRegistry(path=path)

    assert registry2.count() == 1
    data = registry2.get(agent_id.id)
    assert data is not None
    assert data["role"] == "persistent"


def test_load_corrupt_file_returns_empty(tmp_path: Path):
    path = tmp_path / "registry.json"
    path.write_text("this is not valid json")
    registry = AgentRegistry(path=path)

    assert registry.count() == 0


def test_list_all_returns_copy(tmp_path: Path):
    path = tmp_path / "registry.json"
    registry = AgentRegistry(path=path)
    registry.register(Mock(role="dev"))

    snapshot = registry.list_all()
    snapshot["new_key"] = {}  # modify the copy

    assert registry.count() == 1  # original unchanged
