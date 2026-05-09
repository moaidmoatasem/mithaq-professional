"""Tester agent for penetration testing and vulnerability validation."""

from typing import Any

from cherenkov.agents.base_agent import BaseAgent, BaseAgentConfig
from cherenkov.core.config.llm_config import DEFAULT_LLM_MODEL
from cherenkov.core.schemas.cloud_instruction import CloudInstruction


class TesterAgentConfig(BaseAgentConfig):
    """Configuration for Tester agent."""

    def __init__(self, **data):
        """Initialize with tester-specific defaults."""
        super().__init__(
            role=data.get("role", "Security Tester"),
            goal=data.get(
                "goal",
                "Perform penetration testing and validate security vulnerabilities",
            ),
            backstory=data.get(
                "backstory",
                "Expert penetration tester with 10+ years in offensive security, "
                "vulnerability assessment, and security QA. Certified OSCP, CEH with "
                "extensive experience in mobile app pentesting, web app security, and "
                "automated security testing frameworks.",
            ),
            llm_model=data.get("llm_model", DEFAULT_LLM_MODEL),
            verbose=data.get("verbose", True),
            allow_delegation=data.get("allow_delegation", False),
            max_iterations=data.get("max_iterations", 8),
        )


class TesterAgent(BaseAgent):
    """Security tester agent for penetration testing and validation."""

    def __init__(self, config: TesterAgentConfig | None = None):
        """Initialize tester agent.

        Args:
            config: Optional tester configuration. Uses defaults if not provided.
        """
        if config is None:
            config = TesterAgentConfig()
        super().__init__(config)

    def execute(self, task_description: str) -> dict[str, Any]:
        """Execute penetration testing task.

        Args:
            task_description: Description of the testing task

        Returns:
            Dictionary containing test results
        """
        # Sanitize input
        sanitized = self.sanitize_input(task_description)

        # Return test results
        return {
            "task_description": sanitized.sanitized_text,
            "task_type": "penetration_testing",
            "tests_executed": 0,
            "vulnerabilities_confirmed": [],
            "sanitization_applied": sanitized.sanitization_applied,
        }

    def validate_vulnerability(
        self, vuln_id: str, target: str, proof_of_concept: str
    ) -> CloudInstruction:
        """Validate if vulnerability is exploitable.

        Args:
            vuln_id: Vulnerability identifier
            target: Target system/application
            proof_of_concept: PoC description

        Returns:
            CloudInstruction for vulnerability validation
        """
        # Sanitize target
        sanitized_target = self.sanitize_input(target)

        reasoning = f"Validating exploitability of {vuln_id} with proof-of-concept testing"

        return self.create_instruction(
            task_id=f"validate-{vuln_id.replace('-', '')}",
            action="validate_cve",
            target=sanitized_target.sanitized_text[:100],
            confidence=0.91,
            reasoning=reasoning,
        )

    def perform_web_pentest(self, url: str, test_types: list[str]) -> CloudInstruction:
        """Perform web application penetration testing.

        Args:
            url: Target URL
            test_types: List of test types (SQLi, XSS, CSRF, etc.)

        Returns:
            CloudInstruction for web pentesting
        """
        # Sanitize URL
        sanitized_url = self.sanitize_input(url)

        reasoning = (
            f"Web application penetration testing. "
            f"Test coverage: {len(test_types)} security checks"
        )

        return self.create_instruction(
            task_id=f"webtest-{hash(url) % 10000}",
            action="web_recon",
            target=sanitized_url.sanitized_text[:100],
            confidence=0.88,
            reasoning=reasoning,
        )

    def fuzz_api_endpoint(
        self, endpoint: str, http_method: str, parameters: list[str]
    ) -> CloudInstruction:
        """Fuzz API endpoint for vulnerabilities.

        Args:
            endpoint: API endpoint path
            http_method: HTTP method (GET, POST, PUT, DELETE, etc.)
            parameters: List of parameters to fuzz

        Returns:
            CloudInstruction for API fuzzing
        """
        # Sanitize endpoint
        sanitized_endpoint = self.sanitize_input(endpoint)

        reasoning = (
            f"API fuzzing for {http_method} endpoint. "
            f"Testing {len(parameters)} parameters for input validation"
        )

        return self.create_instruction(
            task_id=f"fuzz-{hash(endpoint + http_method) % 10000}",
            action="web_recon",
            target=sanitized_endpoint.sanitized_text[:100],
            confidence=0.85,
            reasoning=reasoning,
        )

    def execute_audit(self, scope: str, compliance_standard: str) -> CloudInstruction:
        """Execute full security audit.

        Args:
            scope: Audit scope description
            compliance_standard: Standard to audit against (OWASP, PCI-DSS, etc.)

        Returns:
            CloudInstruction for security audit
        """
        reasoning = f"Complete security audit for {compliance_standard} compliance"

        return self.create_instruction(
            task_id=f"audit-{hash(scope + compliance_standard) % 10000}",
            action="complete_audit",
            target=compliance_standard,
            confidence=0.93,
            reasoning=reasoning,
        )
