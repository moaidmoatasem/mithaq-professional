"""Base agent class for cherenkov security framework."""


import hashlib
import json
import time
from abc import ABC, abstractmethod
from typing import Any, Optional

from crewai import Agent
from pydantic import BaseModel, Field

from cherenkov.core.ablation import Sanitizer
from cherenkov.core.config.llm_config import DEFAULT_LLM_MODEL
from cherenkov.core.reasoning_store import ReasoningStore
from cherenkov.core.schemas.cloud_instruction import CloudInstruction
from cherenkov.core.schemas.reasoning_trace import ReasoningTrace
from cherenkov.core.schemas.sanitized_output import SanitizedOutput


class BaseAgentConfig(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
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
    reasoning_store: Optional[ReasoningStore] = Field(default=None, description="Store for reasoning traces")
    tools: list[Any] = Field(default_factory=list, description="List of tools for the agent")


class BaseAgent(ABC):
    """Base class for all cherenkov agents with sanitization and CrewAI integration."""

    def __init__(self, config: BaseAgentConfig):
        """Initialize base agent.

        Args:
            config: Agent configuration
        """
        self.config = config
        self.ablation = Sanitizer()
        self.reasoning_store = config.reasoning_store
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create CrewAI agent instance.

        Returns:
            Configured CrewAI Agent
        """
        wrapped_tools = []
        for tool in getattr(self.config, 'tools', []):
            wrapped_tools.append(self._wrap_tool(tool))

        return Agent(
            role=self.config.role,
            goal=self.config.goal,
            backstory=self.config.backstory,
            llm=self.config.llm_model,  # Pass model string directly
            verbose=self.config.verbose,
            allow_delegation=self.config.allow_delegation,
            max_iter=self.config.max_iterations,
            tools=wrapped_tools,
        )

    def _wrap_tool(self, tool: Any) -> Any:
        """Wrap a tool to inject tracing."""
        # Support for functions and basic callable tools
        if callable(tool):
            # Try to get name from common tool patterns
            tool_name = getattr(tool, 'name', getattr(tool, '__name__', 'unknown_tool'))

            def wrapper(*args, **kwargs):
                # We need to construct a dict for args to log
                call_args = {}
                if args:
                    call_args["args"] = args
                if kwargs:
                    call_args.update(kwargs)

                return self.execute_tool(
                    tool_name=tool_name,
                    args=call_args,
                    reasoning=f"Calling tool {tool_name}",
                    tool_func=tool
                )

            # Copy attributes to fool CrewAI/Langchain
            wrapper.name = tool_name
            wrapper.description = getattr(tool, 'description', '')
            wrapper.args_schema = getattr(tool, 'args_schema', None)
            wrapper.func = tool
            return wrapper

        return tool


    def _trace_tool_call(self, tool_name: str, args: dict, output: Any, latency_ms: int, reasoning: str) -> None:
        if self.reasoning_store is None:
            return

        tool_args_hash = hashlib.sha256(json.dumps(args, sort_keys=True).encode()).hexdigest()
        input_summary = f"Tool: {tool_name}, args_hash: {tool_args_hash}"

        # Scrub output and truncate to 500 chars
        scrubbed_output = self.sanitize_input(str(output)).sanitized_text[:500]

        trace = ReasoningTrace(
            step_type="tool_call",
            tool_name=tool_name,
            tool_args_hash=tool_args_hash,
            input_summary=input_summary,
            output_summary=scrubbed_output,
            reasoning=reasoning,
            latency_ms=latency_ms
        )
        self.reasoning_store.add_trace(trace)

    def _trace_step(self, step_type: str, reasoning: str, input_summary: str, output_summary: str, confidence: Optional[float] = None) -> None:
        if self.reasoning_store is None:
            return

        trace = ReasoningTrace(
            step_type=step_type,
            input_summary=input_summary,
            output_summary=output_summary,
            reasoning=reasoning,
            confidence=confidence
        )
        self.reasoning_store.add_trace(trace)

    def execute_tool(self, tool_name: str, args: dict, reasoning: str, tool_func) -> Any:
        t0 = time.monotonic()
        try:
            output = tool_func(**args)
        except Exception as e:
            output = f"Error: {str(e)}"
            raise
        finally:
            latency_ms = int((time.monotonic() - t0) * 1000)
            self._trace_tool_call(tool_name, args, output, latency_ms, reasoning)
        return output

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
