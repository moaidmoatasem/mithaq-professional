"""Unit tests for ArchitectAgent."""

from cherenkov.agents.architect_agent import ArchitectAgent, ArchitectAgentConfig
from cherenkov.schemas.cloud_instruction import CloudInstruction


class TestArchitectAgent:
    """Test suite for ArchitectAgent."""

    def test_default_initialization(self):
        """Test architect agent with default config."""
        agent = ArchitectAgent()

        assert agent.config.role == "Security Architect"
        assert "threat modeling" in agent.config.goal.lower()
        assert agent.ablation is not None

    def test_custom_initialization(self):
        """Test architect agent with custom config."""
        config = ArchitectAgentConfig(
            llm_model="ollama/llama3.2:3b",
            max_iterations=10,
        )

        agent = ArchitectAgent(config)

        assert agent.config.llm_model == "ollama/llama3.2:3b"
        assert agent.config.max_iterations == 10

    def test_execute_task(self):
        """Test task execution."""
        agent = ArchitectAgent()

        result = agent.execute("Analyze mobile app security architecture")

        assert "task_description" in result
        assert "analysis_type" in result
        assert result["analysis_type"] == "architecture_review"

    def test_execute_sanitizes_input(self):
        """Test that execute sanitizes sensitive data."""
        agent = ArchitectAgent()

        result = agent.execute("Check AWS key AKIAIOSFODNN7EXAMPLE in architecture")

        assert result["sanitization_applied"] is True
        assert "AKIA" not in result["task_description"]

    def test_analyze_threat_model(self):
        """Test threat model analysis."""
        agent = ArchitectAgent()

        instruction = agent.analyze_threat_model(
            system_description="Android banking app with biometric authentication",
            attack_vectors=["Man-in-the-Middle", "Root detection"],
        )

        assert isinstance(instruction, CloudInstruction)
        assert instruction.action == "analyze_threat_model"
        assert "threat-model-" in instruction.task_id
        assert instruction.confidence == 0.85

    def test_validate_cve(self):
        """Test CVE validation."""
        agent = ArchitectAgent()

        instruction = agent.validate_cve(
            cve_id="CVE-2024-1234",
            system_context="React Native app using vulnerable WebView component",
        )

        assert isinstance(instruction, CloudInstruction)
        assert instruction.action == "validate_cve"
        assert instruction.target == "CVE-2024-1234"
        assert "cve-validate-" in instruction.task_id

    def test_design_security_architecture(self):
        """Test security architecture design."""
        agent = ArchitectAgent()

        instruction = agent.design_security_architecture(
            requirements=["Zero-trust model", "End-to-end encryption", "MFA"],
            constraints=["Mobile-first", "Offline support"],
        )

        assert isinstance(instruction, CloudInstruction)
        assert instruction.action == "design_architecture"
        assert instruction.target == "security_system"
        assert "arch-design-" in instruction.task_id

    def test_threat_model_sanitizes_secrets(self):
        """Test threat model sanitizes secrets in target."""
        agent = ArchitectAgent()

        instruction = agent.analyze_threat_model(
            system_description="API with JWT authentication token",
            attack_vectors=["Token theft", "Replay attacks"],
        )

        # Target should be sanitized (no JWT in target)
        assert "eyJhbGci" not in instruction.target
        assert isinstance(instruction, CloudInstruction)

    def test_capabilities(self):
        """Test agent capabilities reporting."""
        agent = ArchitectAgent()

        capabilities = agent.get_capabilities()

        assert capabilities["role"] == "Security Architect"
        assert capabilities["sanitization_enabled"] is True
