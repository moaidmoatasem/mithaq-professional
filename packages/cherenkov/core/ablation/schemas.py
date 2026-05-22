# packages/cherenkov/core/ablation/schemas.py
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Telemetry(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    timestamp: datetime = Field(default_factory=get_utc_now)
    module: str = Field(..., description="The component reporting telemetry")
    action: str = Field(..., description="The action taken")
    status: str = Field(..., description="Outcome status")
    metadata: Optional[Dict[str, Any]] = Field(default=None)


class RedactionResult(BaseModel):
    original_length: int = Field(..., ge=0)
    redacted_length: int = Field(..., ge=0)
    redacted_fields: List[str] = Field(default_factory=list)
    is_successful: bool = Field(...)


class SanitizedFinding(BaseModel):
    model_config = ConfigDict(strict=True)

    finding_id: str = Field(...)
    scanner_name: str = Field(...)
    severity: str = Field(..., pattern="^(INFO|LOW|MEDIUM|HIGH|CRITICAL)$")
    sanitized_payload: Dict[str, Any]
    redaction_metrics: RedactionResult
    is_sanitized: bool = Field(default=False)
