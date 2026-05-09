"""Shared dataclasses for the orchestration module."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class WorkflowResult:
    """Result of workflow execution."""
    success: bool
    outputs: Dict[str, Any]
    duration: float
    errors: Optional[List[str]] = None


@dataclass
class AgentID:
    """Unique identifier for registered agent."""
    id: str
    role: str
