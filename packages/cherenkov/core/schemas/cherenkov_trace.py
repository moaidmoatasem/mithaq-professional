from datetime import datetime, timezone
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class CherenkovTrace(BaseModel):
    trace_id: str = Field(..., description="Unique identifier for the trace")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    target: str = Field(..., description="Target being scanned/analyzed")
    mode: str = Field(..., description="Execution mode (e.g., hybrid, local_only)")
    findings: List[Dict[str, str]] = Field(default_factory=list, description="List of findings")
    cryptographic_anchor: Optional[Dict[str, str]] = Field(None, description="Cryptographic proofs")

    model_config = {"extra": "forbid"}
