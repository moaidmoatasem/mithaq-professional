"""Base agent class for cherenkov security framework."""

from abc import ABC, abstractmethod
from typing import Any

from crewai import Agent
from pydantic import BaseModel, Field

from cherenkov.core.config.llm_config import DEFAULT_LLM_MODEL
from cherenkov.core.ablation import Sanitizer
from cherenkov.core.schemas.cloud_instruction import CloudInstruction
from cherenkov.core.schemas.sanitized_output import SanitizedOutput


class BaseAgentConfig(BaseModel):
    """Configuration for base agent."""

    role: str = Field(..., description="Agent role (e.g., 'Security Architect')")
    goal: str = Field(..., description="Primary goal of the agent")
    backstory: str = Field(..., description="Agent's background and expertise")
    llm_model: str = Field(
        default=DEFAULT_LLM_MODEL, description="LLM model (format: provider/model)"
    )
    verbose: bool = Field(default=True, description="Enable verbose logging")
    allow_delegation: bool = Field(
        default=False, description="Allow task delegation to other agents"
    )
    max_iterations: int = Field(default=5, description="Max task iterations")


class BaseAgent(ABC):
    """Base class for all cherenkov agents with sanitization and CrewAI integration."""

    def __init__(self, config: BaseAgentConfig):
        """Initialize base agent.

        Args:
            config: Agent configuration
        """
        self.config = config
        self.ablation = Sanitizer()
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create CrewAI agent instance.

        Returns:
            Configured CrewAI Agent
        """
        return Agent(
            role=self.config.role,
            goal=self.config.goal,
            backstory=self.config.backstory,
            llm=self.config.llm_model,  # Pass model string directly
            verbose=self.config.verbose,
            allow_delegation=self.config.allow_delegation,
            max_iter=self.config.max_iterations,
        )

    def sanitize_input(self, text: str) -> SanitizedOutput:
        """Sanitize input text before processing.

        Args:
            text: Raw input text

        Returns:
            Sanitization result
        """
        return self.ablation.sanitize(text)

    def create_instruction(
        self,
        task_id: str,
        action: str,
        target: str,
        confidence: float,
        reasoning: str,
    ) -> CloudInstruction:
        """Create sanitized cloud instruction.

        Args:
            task_id: Unique task identifier
            action: Action to perform
            target: Target of the action
            confidence: Confidence score (0.0-1.0)
            reasoning: Reasoning behind the action

        Returns:
            Sanitized CloudInstruction
        """
        # Sanitize reasoning before creating instruction
        sanitized = self.sanitize_input(reasoning)

        return CloudInstruction(
            task_id=task_id,
            action=action,
            target=target,
            confidence=confidence,
            reasoning=sanitized.sanitized_text,
        )

    @abstractmethod
    def execute(self, task_description: str) -> Any:
        """Execute agent task.

        Args:
            task_description: Description of the task to execute

        Returns:
            Task execution result
        """
        pass

    def get_capabilities(self) -> dict[str, Any]:
        """Get agent capabilities and metadata.

        Returns:
            Dictionary of agent capabilities
        """
        return {
            "role": self.config.role,
            "goal": self.config.goal,
            "llm_model": self.config.llm_model,
            "max_iterations": self.config.max_iterations,
            "sanitization_enabled": True,
        }
