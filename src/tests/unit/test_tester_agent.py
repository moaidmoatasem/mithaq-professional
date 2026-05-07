"""Unit tests for TesterAgent."""

from mithaq.agents.tester_agent import TesterAgent, TesterAgentConfig
from mithaq.schemas.cloud_instruction import CloudInstruction


class TestTesterAgent:
    """Test suite for TesterAgent."""

    def test_default_initialization(self):
        """Test tester agent with default config."""
        agent = TesterAgent()

        assert agent.config.role == "Security Tester"
        assert "penetration testing" in agent.config.goal.lower()
        assert agent.config.max_iterations == 8
        assert agent.sanitizer is not None

    def test_custom_initialization(self):
        """Test tester agent with custom config."""
        config = TesterAgentConfig(
            llm_model="ollama/llama3.2:3b",
            max_iterations=12,
        )

        agent = TesterAgent(config)

        assert agent.config.llm_model == "ollama/llama3.2:3b"
        assert agent.config.max_iterations == 12

    def test_execute_task(self):
        """Test task execution."""
        agent = TesterAgent()

        result = agent.execute("Perform SQLi testing on login form")

        assert "task_description" in result
        assert "task_type" in result
        assert result["task_type"] == "penetration_testing"

    def test_execute_sanitizes_input(self):
        """Test that execute sanitizes sensitive data."""
        agent = TesterAgent()

        result = agent.execute("Test API with token eyJhbGciOiJIUzI1NiJ9.test.sig")

        assert result["sanitization_applied"] is True
        assert "eyJhbGci" not in result["task_description"]

    def test_validate_vulnerability(self):
        """Test vulnerability validation."""
        agent = TesterAgent()

        instruction = agent.validate_vulnerability(
            vuln_id="CVE-2024-5678",
            target="mobile-banking-app",
            proof_of_concept="SQL injection in login endpoint",
        )

        assert isinstance(instruction, CloudInstruction)
        assert instruction.action == "validate_cve"
        assert "validate-" in instruction.task_id
        assert instruction.confidence == 0.91

    def test_perform_web_pentest(self):
        """Test web application penetration testing."""
        agent = TesterAgent()

        instruction = agent.perform_web_pentest(
            url="https://example.com/app",
            test_types=["SQLi", "XSS", "CSRF", "Directory Traversal"],
        )

        assert isinstance(instruction, CloudInstruction)
        assert instruction.action == "web_recon"
        assert "webtest-" in instruction.task_id
        assert "4 security checks" in instruction.reasoning

    def test_fuzz_api_endpoint(self):
        """Test API endpoint fuzzing."""
        agent = TesterAgent()

        instruction = agent.fuzz_api_endpoint(
            endpoint="/api/v1/users",
            http_method="POST",
            parameters=["username", "email", "password"],
        )

        assert isinstance(instruction, CloudInstruction)
        assert instruction.action == "web_recon"
        assert "fuzz-" in instruction.task_id
        assert "POST" in instruction.reasoning

    def test_execute_audit(self):
        """Test security audit execution."""
        agent = TesterAgent()

        instruction = agent.execute_audit(
            scope="Web application and REST API",
            compliance_standard="OWASP Top 10",
        )

        assert isinstance(instruction, CloudInstruction)
        assert instruction.action == "complete_audit"
        assert "audit-" in instruction.task_id
        assert "OWASP Top 10" in instruction.reasoning

    def test_validate_sanitizes_target(self):
        """Test vulnerability validation sanitizes target."""
        agent = TesterAgent()

        instruction = agent.validate_vulnerability(
            vuln_id="CVE-2024-9999",
            target="app-AKIAIOSFODNN7EXAMPLE-prod",
            proof_of_concept="RCE via command injection",
        )

        # Target should be sanitized
        assert "[REDACTED]" in instruction.target
        assert "AKIA" not in instruction.target

    def test_web_pentest_sanitizes_url(self):
        """Test web pentest sanitizes URL with secrets."""
        agent = TesterAgent()

        instruction = agent.perform_web_pentest(
            url="https://api.example.com?token=eyJhbGciOiJIUzI1NiJ9.data.sig",
            test_types=["Authentication bypass"],
        )

        # URL should be sanitized
        assert "[REDACTED]" in instruction.target
        assert "eyJhbGci" not in instruction.target

    def test_capabilities(self):
        """Test agent capabilities reporting."""
        agent = TesterAgent()

        capabilities = agent.get_capabilities()

        assert capabilities["role"] == "Security Tester"
        assert capabilities["sanitization_enabled"] is True
        assert capabilities["max_iterations"] == 8

