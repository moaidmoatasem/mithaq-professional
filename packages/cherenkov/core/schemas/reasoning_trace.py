import hashlib
import json
from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ReasoningTrace(BaseModel):
    """Trace recording the reasoning steps of agents and LLMs."""

    trace_id: str = Field(..., description="UUID4 for the trace")
    agent_id: str
    agent_role: str
    session_id: str
    step_index: int
    step_type: Literal["plan", "tool_call", "llm_inference", "delegation", "verdict"]
    input_summary: str = Field(..., description="Ablation-scrubbed input summary")
    output_summary: str = Field(..., description="Ablation-scrubbed output summary")
    reasoning: str = Field(..., description="LLM's explanation of why it took this step")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    model_backend: Optional[str] = None
    latency_ms: Optional[int] = None
    tool_name: Optional[str] = None
    tool_args_hash: Optional[str] = Field(
        None, description="SHA-256 of tool args, not the args themselves"
    )
    sha256_anchor: str = Field(
        ..., description="SHA-256 of the serialized trace fields excluding this field"
    )
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(extra="forbid")

    def compute_hash(self) -> str:
        """Compute the SHA-256 anchor for this trace."""
        data = self.model_dump(exclude={"sha256_anchor"}, mode="json")
        # Ensure deterministic JSON serialization
        serialized = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def verify_anchor(self) -> bool:
        """Verify that the sha256_anchor matches the computed hash."""
        return self.sha256_anchor == self.compute_hash()
