from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ReasoningTrace(BaseModel):
    step_type: str = Field(..., description="Type of inference step, e.g., llm_inference")
    input_summary: str = Field(..., description="Ablation-scrubbed first 500 chars of the prompt")
    output_summary: str = Field(
        ..., description="Ablation-scrubbed first 500 chars of the completion"
    )
    reasoning: str = Field(..., description="Extracted reasoning or '[implicit]'")
    model_backend: str = Field(..., description="The backend string that was actually used")
    latency_ms: float = Field(..., description="Wall-clock ms of the inference call")
    confidence: Optional[float] = Field(None, description="Confidence score if available")
    sha256_anchor: str = Field(..., description="SHA-256 of the serialized trace")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Timestamp of the trace"
    )
