"""Unit tests for Red Team agent."""

import pytest
from cherenkov.agents.red_team import RedTeamAgent, RedTeamAgentConfig
from cherenkov.core.schemas.cloud_instruction import CloudInstruction


def test_red_team_agent_config_defaults():
    """Test that RedTeamAgentConfig has correct default values."""
    config = RedTeamAgentConfig()
    assert config.role == "Red Team Specialist"
    assert "offensive security audits" in config.goal
    assert "offensive security expert" in config.backstory
    assert config.llm_model == "red-team"
    assert config.verbose is True
    assert config.allow_delegation is False
    assert config.max_iterations == 5


def test_red_team_agent_config_custom():
    """Test custom configuration parameters."""
    config = RedTeamAgentConfig(
        role="Hacker",
        goal="Hack things",
        backstory="Born to hack",
        llm_model="custom-red-model",
        verbose=False,
        allow_delegation=True,
        max_iterations=10,
    )
    assert config.role == "Hacker"
    assert config.goal == "Hack things"
    assert config.backstory == "Born to hack"
    assert config.llm_model == "custom-red-model"
    assert config.verbose is False
    assert config.allow_delegation is True
    assert config.max_iterations == 10


def test_red_team_agent_instantiation():
    """Test successful instantiation and capabilities of RedTeamAgent."""
    agent = RedTeamAgent()
    capabilities = agent.get_capabilities()
    assert capabilities["role"] == "Red Team Specialist"
    assert capabilities["llm_model"] == "red-team"
    assert capabilities["max_iterations"] == 5
    assert capabilities["sanitization_enabled"] is True


def test_red_team_agent_execute_stub():
    """Test execute stub behavior with sanitization."""
    agent = RedTeamAgent()
    result = agent.execute("Simulate a SQL injection payload on http://test.local")
    assert isinstance(result, dict)
    assert "Simulate a SQL injection payload" in result["task_description"]
    assert result["task_type"] == "offensive_simulation"
    assert result["exploit_generated"] is False
    assert isinstance(result["payloads_crafted"], list)


def test_red_team_agent_plan_attack_path():
    """Test that planning an attack path generates a proper CloudInstruction."""
    agent = RedTeamAgent()
    instruction = agent.plan_attack_path(
        target_architecture="External facing DMZ with open APIs",
        entry_points=["/api/v1/login", "/api/v1/upload"],
    )
    assert isinstance(instruction, CloudInstruction)
    assert instruction.action == "complete_audit"
    assert "DMZ" in instruction.target
    assert instruction.confidence == 0.88
    assert "Entry vectors" in instruction.reasoning
