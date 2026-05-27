"""Unit tests for SecOps agent."""

import pytest
from cherenkov.agents.secops import SecOpsAgent, SecOpsAgentConfig
from cherenkov.core.schemas.cloud_instruction import CloudInstruction


def test_secops_agent_config_defaults():
    """Test that SecOpsAgentConfig has correct default values."""
    config = SecOpsAgentConfig()
    assert config.role == "SecOps Specialist"
    assert "compliance" in config.goal
    assert "compliance officer" in config.backstory
    assert config.llm_model == "secops"
    assert config.verbose is True
    assert config.allow_delegation is False
    assert config.max_iterations == 5


def test_secops_agent_config_custom():
    """Test custom configuration parameters."""
    config = SecOpsAgentConfig(
        role="Compliance Auditor",
        goal="Audit compliance frameworks",
        backstory="Born to audit",
        llm_model="custom-secops-model",
        verbose=False,
        allow_delegation=True,
        max_iterations=10,
    )
    assert config.role == "Compliance Auditor"
    assert config.goal == "Audit compliance frameworks"
    assert config.backstory == "Born to audit"
    assert config.llm_model == "custom-secops-model"
    assert config.verbose is False
    assert config.allow_delegation is True
    assert config.max_iterations == 10


def test_secops_agent_instantiation():
    """Test successful instantiation and capabilities of SecOpsAgent."""
    agent = SecOpsAgent()
    capabilities = agent.get_capabilities()
    assert capabilities["role"] == "SecOps Specialist"
    assert capabilities["llm_model"] == "secops"
    assert capabilities["max_iterations"] == 5
    assert capabilities["sanitization_enabled"] is True


def test_secops_agent_execute_stub():
    """Test execute stub behavior with sanitization."""
    agent = SecOpsAgent()
    result = agent.execute("Map SQL injection finding to CBE compliance controls")
    assert isinstance(result, dict)
    assert "Map SQL injection finding" in result["task_description"]
    assert result["task_type"] == "compliance_mapping"
    assert result["compliance_mapped"] is False
    assert isinstance(result["remediations_drafted"], list)


def test_secops_agent_map_compliance():
    """Test that mapping compliance generates a proper CloudInstruction."""
    agent = SecOpsAgent()
    instruction = agent.map_compliance(
        finding_description="Stored Cross-Site Scripting (XSS) in user profile comments",
        framework="EGY-FIN CSF",
    )
    assert isinstance(instruction, CloudInstruction)
    assert instruction.action == "complete_audit"
    assert "Cross-Site Scripting" in instruction.target
    assert instruction.confidence == 0.90
    assert "EGY-FIN CSF" in instruction.reasoning
