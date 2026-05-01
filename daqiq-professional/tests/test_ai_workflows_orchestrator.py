from unittest.mock import Mock, patch
from daqiq.ai_workflows_orchestrator import orchestrate_ai_workflows


def test_orchestrate_ai_workflows_returns_summary():
    def echo_agent(payload):
        return {"echo": payload}

    context = {
        "project_name": "Test Project",
        "roadmap": [
            {"name": "Echo step", "agent": "echo", "input": {"message": "hello"}},
            {"name": "No agent step"},
            {"name": "Unknown agent step", "agent": "missing"},
        ],
        "agents": {
            "echo": echo_agent,
        },
    }

    summary = orchestrate_ai_workflows(context)

    assert summary["project_name"] == "Test Project"
    assert summary["total_steps"] == 3

    steps = summary["steps"]
    assert len(steps) == 3

    # Step 1: executed by echo agent successfully
    assert steps[0]["name"] == "Echo step"
    assert steps[0]["agent"] == "echo"
    assert steps[0]["status"] == "completed"
    assert steps[0]["result"] == {"echo": {"message": "hello"}}
    assert steps[0]["error"] is None

    # Step 2: no agent specified -> skipped
    assert steps[1]["name"] == "No agent step"
    assert steps[1]["agent"] is None
    assert steps[1]["status"] == "skipped"
    assert steps[1]["result"] is None
    assert steps[1]["error"] is not None

    # Step 3: unknown agent -> error
    assert steps[2]["name"] == "Unknown agent step"
    assert steps[2]["agent"] == "missing"
    assert steps[2]["status"] == "error"
    assert steps[2]["result"] is None
    assert steps[2]["error"] is not None

def test_orchestrator_with_mock():
    """Test orchestrator without real LLM calls"""
    with patch('crewai.LLM') as mock_llm:
        mock_llm.return_value = Mock()
        # Test orchestrator initialization
        # orchestrator = WorkflowOrchestrator()
        # assert orchestrator is not None
        pass  # Placeholder for actual test
