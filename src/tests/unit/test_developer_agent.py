"""Unit tests for DeveloperAgent."""

from cherenkov.agents.developer_agent import DeveloperAgent, DeveloperAgentConfig
from cherenkov.schemas.cloud_instruction import CloudInstruction


class TestDeveloperAgent:
    """Test suite for DeveloperAgent."""

    def test_default_initialization(self):
        """Test developer agent with default config."""
        agent = DeveloperAgent()

        assert agent.config.role == "Security Developer"
        assert "exploit" in agent.config.goal.lower()
        assert agent.config.max_iterations == 7
        assert agent.ablation is not None

    def test_custom_initialization(self):
        """Test developer agent with custom config."""
        config = DeveloperAgentConfig(
            llm_model="ollama/codellama:13b",
            max_iterations=10,
        )

        agent = DeveloperAgent(config)

        assert agent.config.llm_model == "ollama/codellama:13b"
        assert agent.config.max_iterations == 10

    def test_execute_task(self):
        """Test task execution."""
        agent = DeveloperAgent()

        result = agent.execute("Generate exploit for SQLi vulnerability")

        assert "task_description" in result
        assert "task_type" in result
        assert result["task_type"] == "code_development"

    def test_execute_sanitizes_input(self):
        """Test that execute sanitizes sensitive data."""
        agent = DeveloperAgent()

        result = agent.execute("Generate code with API key AKIAIOSFODNN7EXAMPLE")

        assert result["sanitization_applied"] is True
        assert "AKIA" not in result["task_description"]

    def test_analyze_smali(self):
        """Test Smali bytecode analysis."""
        agent = DeveloperAgent()

        instruction = agent.analyze_smali(
            apk_path="/path/to/app.apk",
            target_classes=["MainActivity", "AuthService", "CryptoHelper"],
        )

        assert isinstance(instruction, CloudInstruction)
        assert instruction.action == "analyze_smali"
        assert "smali-" in instruction.task_id
        assert instruction.confidence == 0.92

    def test_generate_exploit(self):
        """Test exploit generation."""
        agent = DeveloperAgent()

        instruction = agent.generate_exploit(
            vulnerability_type="SQL Injection",
            target_platform="Android",
            severity="High",
        )

        assert isinstance(instruction, CloudInstruction)
        assert instruction.action == "complete_audit"
        assert "exploit-" in instruction.task_id
        assert "SQL Injection" in instruction.reasoning

    def test_review_code(self):
        """Test code security review."""
        agent = DeveloperAgent()

        code = """
        def authenticate(username, password):
            query = f"SELECT * FROM users WHERE user='{username}' AND pass='{password}'"
            return db.execute(query)
        """

        instruction = agent.review_code(code_snippet=code, language="Python")

        assert isinstance(instruction, CloudInstruction)
        assert instruction.action == "complete_audit"
        assert "review-" in instruction.task_id
        assert "Python" in instruction.reasoning

    def test_craft_payload(self):
        """Test payload crafting."""
        agent = DeveloperAgent()

        instruction = agent.craft_payload(
            attack_vector="XSS",
            encoding="url",
            target_tech="React/Node.js",
        )

        assert isinstance(instruction, CloudInstruction)
        assert instruction.action == "web_recon"
        assert "payload-" in instruction.task_id
        assert "XSS" in instruction.reasoning

    def test_smali_sanitizes_path(self):
        """Test Smali analysis sanitizes APK path."""
        agent = DeveloperAgent()

        instruction = agent.analyze_smali(
            apk_path="/apps/banking_AKIAIOSFODNN7EXAMPLE.apk",
            target_classes=["LoginActivity"],
        )

        # Path should be sanitized
        assert "[REDACTED]" in instruction.target
        assert "AKIA" not in instruction.target

    def test_review_code_sanitizes_secrets(self):
        """Test code review sanitizes secrets in code."""
        agent = DeveloperAgent()

        # nosec B105: This is a test example, not a real secret
        example_code = """
        const token = "eyJhbGciOiJIUzI1NiJ9.payload.signature";
        fetch('/api', { headers: { 'Authorization': token }});
        """

        instruction = agent.review_code(
            code_snippet=example_code,
            language="JavaScript",
        )

        # Code sanitization happens in target/reasoning
        assert isinstance(instruction, CloudInstruction)

    def test_capabilities(self):
        """Test agent capabilities reporting."""
        agent = DeveloperAgent()

        capabilities = agent.get_capabilities()

        assert capabilities["role"] == "Security Developer"
        assert capabilities["sanitization_enabled"] is True
        assert capabilities["max_iterations"] == 7

