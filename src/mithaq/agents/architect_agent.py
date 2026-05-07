"""Architect agent for security system design and threat modeling."""

from typing import Any

from mithaq.agents.base_agent import BaseAgent, BaseAgentConfig
from mithaq.config import DEFAULT_LLM_MODEL
from mithaq.schemas.cloud_instruction import CloudInstruction


class ArchitectAgentConfig(BaseAgentConfig):
    """Configuration for Architect agent."""

    def __init__(self, **data):
        """Initialize with architect-specific defaults."""
        super().__init__(
            role=data.get("role", "Security Architect"),
            goal=data.get(
                "goal",
                "Design secure systems and perform threat modeling analysis",
            ),
            backstory=data.get(
                "backstory",
                "Expert security architect with 15+ years experience in threat modeling, "
                "security architecture design, and CVE analysis. Specializes in mobile app "
                "security, cloud infrastructure, and zero-trust architectures.",
            ),
            llm_model=data.get("llm_model", DEFAULT_LLM_MODEL),
            verbose=data.get("verbose", True),
            allow_delegation=data.get("allow_delegation", False),
            max_iterations=data.get("max_iterations", 5),
        )


class ArchitectAgent(BaseAgent):
    """Security architect agent for system design and threat modeling."""

    def __init__(self, config: ArchitectAgentConfig | None = None):
        """Initialize architect agent.

        Args:
            config: Optional architect configuration. Uses defaults if not provided.
        """
        if config is None:
            config = ArchitectAgentConfig()
        super().__init__(config)

    def execute(self, task_description: str) -> dict[str, Any]:
        """Execute architecture analysis task.

        Args:
            task_description: Description of the architecture task

        Returns:
            Dictionary containing analysis results
        """
        # Sanitize input
        sanitized = self.sanitize_input(task_description)

        # Return analysis results (CrewAI Task would be created in Crew orchestration)
        return {
            "task_description": sanitized.sanitized_text,
            "analysis_type": "architecture_review",
            "threats_identified": [],
            "recommendations": [],
            "sanitization_applied": sanitized.sanitization_applied,
        }

    def analyze_threat_model(
        self, system_description: str, attack_vectors: list[str]
    ) -> CloudInstruction:
        """Analyze system threat model.

        Args:
            system_description: Description of the system to analyze
            attack_vectors: List of potential attack vectors

        Returns:
            CloudInstruction with threat analysis
        """
        # Sanitize system description for target field
        sanitized_target = self.sanitize_input(system_description)

        reasoning = (
            f"Threat model analysis for mobile/web application. "
            f"Attack vectors considered: {len(attack_vectors)} potential threats"
        )

        return self.create_instruction(
            task_id=f"threat-model-{hash(system_description) % 10000}",
            action="analyze_threat_model",
            target=sanitized_target.sanitized_text[:100],  # Sanitized + truncated
            confidence=0.85,
            reasoning=reasoning,
        )

    def validate_cve(self, cve_id: str, system_context: str) -> CloudInstruction:
        """Validate CVE relevance to system.

        Args:
            cve_id: CVE identifier (e.g., CVE-2024-1234)
            system_context: Context of the system being analyzed

        Returns:
            CloudInstruction for CVE validation
        """
        reasoning = f"Validating {cve_id} applicability to target application"

        return self.create_instruction(
            task_id=f"cve-validate-{cve_id.replace('-', '')}",
            action="validate_cve",
            target=cve_id,
            confidence=0.9,
            reasoning=reasoning,
        )

    def design_security_architecture(
        self, requirements: list[str], constraints: list[str]
    ) -> CloudInstruction:
        """Design security architecture.

        Args:
            requirements: List of security requirements
            constraints: List of design constraints

        Returns:
            CloudInstruction for architecture design
        """
        reasoning = (
            f"Security architecture design with {len(requirements)} requirements "
            f"and {len(constraints)} constraints"
        )

        return self.create_instruction(
            task_id=f"arch-design-{hash(''.join(requirements)) % 10000}",
            action="design_architecture",
            target="security_system",
            confidence=0.88,
            reasoning=reasoning,
        )

