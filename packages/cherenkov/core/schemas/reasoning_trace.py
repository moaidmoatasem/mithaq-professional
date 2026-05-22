from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class ReasoningTrace(BaseModel):
    step_type: str = Field(..., description="Type of reasoning step (e.g., tool_call, plan, delegation)")
    tool_name: Optional[str] = Field(None, description="Name of the tool called")
    tool_args_hash: Optional[str] = Field(None, description="SHA-256 hash of the tool arguments")
    input_summary: str = Field(..., description="Summary of input or reasoning")
    output_summary: str = Field(..., description="Summary of output or result")
    reasoning: str = Field(..., description="Reasoning behind this step")
    confidence: Optional[float] = Field(None, description="Confidence score for this step")
    latency_ms: Optional[int] = Field(None, description="Latency in milliseconds")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"extra": "forbid"}
