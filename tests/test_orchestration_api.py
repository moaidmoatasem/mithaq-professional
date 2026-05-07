"""
Tests for Orchestration API
"""
import pytest
from mithaq.orchestration_api import (
    orchestrate_workflow, 
    register_agent, 
    execute_parallel,
    get_workflow_status,
    WorkflowResult,
    AgentID
)
from unittest.mock import Mock, patch

def test_orchestrate_workflow_success():
    """Test successful workflow orchestration"""
    config = {'workflow': 'test', 'agents': ['agent1']}
    result = orchestrate_workflow(config)
    
    assert isinstance(result, WorkflowResult)
    assert result.success is True
    assert result.outputs is not None

def test_orchestrate_workflow_empty_config():
    """Test workflow with empty config"""
    result = orchestrate_workflow({})
    
    assert result.success is False
    assert 'Empty config' in result.errors

def test_register_agent():
    """Test agent registration"""
    mock_agent = Mock()
    mock_agent.role = 'researcher'
    
    agent_id = register_agent(mock_agent)
    
    assert isinstance(agent_id, AgentID)
    assert agent_id.role == 'researcher'
    assert len(agent_id.id) > 0

def test_execute_parallel():
    """Test parallel agent execution"""
    agents = [Mock(), Mock(), Mock()]
    tasks = ['task1', 'task2', 'task3']
    
    results = execute_parallel(agents, tasks)
    
    assert len(results) == 3
    assert all('success' in r for r in results)


def test_workflow_executor_generate_report():
    """Test generating execution report from WorkflowExecutor"""
    from mithaq.orchestration_api import WorkflowExecutor

    config = {
        "name": "test_report_workflow",
        "execution": {"mode": "parallel"}
    }

    executor = WorkflowExecutor(config)
    executor.agents = ["agent1", "agent2"]
    executor.results = [{"task": "t1"}, {"task": "t2"}]

    report = executor.generate_report()

    assert report["workflow"] == "test_report_workflow"
    assert report["agents_used"] == 2
    assert report["tasks_completed"] == 2
    assert report["results"] == [{"task": "t1"}, {"task": "t2"}]

    metrics = report["metrics"]
    assert metrics["agents_deployed"] == 2
    assert metrics["tasks_executed"] == 2
    assert metrics["workflow_name"] == "test_report_workflow"
    assert metrics["execution_mode"] == "parallel"

def test_workflow_executor_generate_report_empty_config():
    """Test generating execution report with empty config"""
    from mithaq.orchestration_api import WorkflowExecutor

    executor = WorkflowExecutor({})
    report = executor.generate_report()

    assert report["workflow"] == "Unknown"
    assert report["agents_used"] == 0
    assert report["tasks_completed"] == 0
    assert report["results"] == []

    metrics = report["metrics"]
    assert metrics["agents_deployed"] == 0
    assert metrics["tasks_executed"] == 0
    assert metrics["workflow_name"] == "unknown"
    assert metrics["execution_mode"] == "sequential"
@patch('mithaq.result_persistence.ResultStore')
def test_get_workflow_status(mock_result_store):
    """Test get_workflow_status calls ResultStore.get_latest"""
    # Configure mock
    mock_store_instance = mock_result_store.return_value
    mock_store_instance.get_latest.return_value = {'status': 'completed', 'result': 'success'}

    # Call function
    result = get_workflow_status('test_workflow_123')

    # Assert
    mock_result_store.assert_called_once()
    mock_store_instance.get_latest.assert_called_once_with('test_workflow_123')
    assert result == {'status': 'completed', 'result': 'success'}

@patch('mithaq.result_persistence.ResultStore')
def test_get_workflow_status_not_found(mock_result_store):
    """Test get_workflow_status handles missing workflows"""
    # Configure mock to return None
    mock_store_instance = mock_result_store.return_value
    mock_store_instance.get_latest.return_value = None

    # Call function
    result = get_workflow_status('nonexistent_workflow')

    # Assert
    mock_result_store.assert_called_once()
    mock_store_instance.get_latest.assert_called_once_with('nonexistent_workflow')
    assert result is None
