"""Unit tests for BaseAgent."""

from cherenkov.agents.base_agent import BaseAgent, BaseAgentConfig
from cherenkov.schemas.cloud_instruction import CloudInstruction
from cherenkov.schemas.sanitized_output import SanitizedOutput


class ConcreteTestAgent(BaseAgent):
    """Concrete test implementation of BaseAgent."""

    def execute(self, task_description: str) -> str:
        """Simple test execution."""
        return f"Executed: {task_description}"


class TestBaseAgent:
    """Test suite for BaseAgent."""

    def test_agent_initialization(self):
        """Test agent can be initialized with config."""
        config = BaseAgentConfig(
            role="Test Agent",
            goal="Testing functionality",
            backstory="A test agent for unit testing",
        )

        agent = ConcreteTestAgent(config)

        assert agent.config.role == "Test Agent"
        assert agent.ablation is not None
        assert agent.agent is not None
        assert agent.agent.role == "Test Agent"

    def test_sanitize_input(self):
        """Test input sanitization works."""
        config = BaseAgentConfig(
            role="Security Tester",
            goal="Test sanitization",
            backstory="Security-focused test agent",
        )

        agent = ConcreteTestAgent(config)
        result = agent.sanitize_input("Found key AKIAIOSFODNN7EXAMPLE in config")

        assert isinstance(result, SanitizedOutput)
        assert result.sanitization_applied is True
        assert "[REDACTED]" in result.sanitized_text

    def test_create_instruction_with_sanitization(self):
        """Test instruction creation sanitizes reasoning."""
        config = BaseAgentConfig(
            role="Security Analyst",
            goal="Create secure instructions",
            backstory="Analyst creating sanitized instructions",
        )

        agent = ConcreteTestAgent(config)
        instruction = agent.create_instruction(
            task_id="test-001",
            action="analyze_smali",
            target="app.apk",
            confidence=0.9,
            reasoning="Found AWS key AKIAIOSFODNN7EXAMPLE",
        )

        assert isinstance(instruction, CloudInstruction)
        assert instruction.task_id == "test-001"
        assert "[REDACTED]" in instruction.reasoning
        assert "AKIA" not in instruction.reasoning

    def test_get_capabilities(self):
        """Test capabilities reporting."""
        config = BaseAgentConfig(
            role="Capability Tester",
            goal="Test capability reporting",
            backstory="Agent testing capabilities",
            llm_model="ollama/llama3.2:3b",
        )

        agent = ConcreteTestAgent(config)
        capabilities = agent.get_capabilities()

        assert capabilities["role"] == "Capability Tester"
        assert capabilities["llm_model"] == "ollama/llama3.2:3b"
        assert capabilities["sanitization_enabled"] is True
        assert "max_iterations" in capabilities

    def test_execute_abstract_method(self):
        """Test execute method works in implementation."""
        config = BaseAgentConfig(
            role="Executor",
            goal="Execute tasks",
            backstory="Task execution agent",
        )

        agent = ConcreteTestAgent(config)
        result = agent.execute("Test task")

        assert result == "Executed: Test task"

    def test_custom_llm_config(self):
        """Test custom LLM configuration."""
        config = BaseAgentConfig(
            role="Custom LLM Agent",
            goal="Test custom LLM",
            backstory="Agent with custom LLM settings",
            llm_model="ollama/deepseek-r1:7b",
        )

        agent = ConcreteTestAgent(config)

        # Verify config stored correctly
        assert agent.config.llm_model == "ollama/deepseek-r1:7b"

        # Verify LLM object created (CrewAI converts string to LLM internally)
        assert agent.agent.llm is not None
        assert hasattr(agent.agent.llm, "model")
        assert agent.agent.llm.model == "deepseek-r1:7b"
