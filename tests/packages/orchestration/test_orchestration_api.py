"""
Tests for Orchestration API
"""

from unittest.mock import Mock, PropertyMock, patch

from cherenkov.orchestration.orchestration_api import (
    AgentID,
    WorkflowResult,
    execute_parallel,
    get_workflow_status,
    orchestrate_workflow,
    register_agent,
)


def test_orchestrate_workflow_success():
    """Test successful workflow orchestration"""
    config = {"workflow": "test", "agents": ["agent1"]}
    result = orchestrate_workflow(config)

    assert isinstance(result, WorkflowResult)
    assert result.success is True
    assert result.outputs is not None


def test_orchestrate_workflow_empty_config():
    """Test workflow with empty config"""
    result = orchestrate_workflow({})

    assert result.success is False
    assert "Empty config" in result.errors


def test_register_agent():
    """Test agent registration"""
    mock_agent = Mock()
    mock_agent.role = "researcher"

    agent_id = register_agent(mock_agent)

    assert isinstance(agent_id, AgentID)
    assert agent_id.role == "researcher"
    assert len(agent_id.id) > 0


def test_execute_parallel():
    """Test parallel agent execution"""
    agents = [Mock(), Mock(), Mock()]
    tasks = ["task1", "task2", "task3"]

    results = execute_parallel(agents, tasks)

    assert len(results) == 3
    assert all("success" in r for r in results)


@patch("cherenkov.orchestration.orchestration_api._scheduler")
def test_get_workflow_status(mock_scheduler):
    """Test get_workflow_status calls scheduler.get_status"""
    mock_scheduler.get_status.return_value = {"status": "completed", "result": "success"}

    result = get_workflow_status("test_workflow_123")

    mock_scheduler.get_status.assert_called_once_with("test_workflow_123")
    assert result == {"status": "completed", "result": "success"}


@patch("cherenkov.orchestration.orchestration_api._scheduler")
def test_get_workflow_status_not_found(mock_scheduler):
    """Test get_workflow_status handles missing workflows"""
    mock_scheduler.get_status.return_value = None

    result = get_workflow_status("nonexistent_workflow")

    mock_scheduler.get_status.assert_called_once_with("nonexistent_workflow")
    assert result is None
