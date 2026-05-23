# packages/cherenkov/core/ablation/schemas.py
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Telemetry(BaseModel):
    """
    Tracks the internal operations of the MEISSNER and ABLATION gates.
    Must not contain raw target data.
    """
    model_config = ConfigDict(strict=True, extra="forbid")

    timestamp: datetime = Field(default_factory=get_utc_now)
    module: str = Field(..., description="The component reporting telemetry (e.g., 'ablation_bridge')")
    action: str = Field(..., description="The action taken (e.g., 'redact_payload', 'drop_packet')")
    status: str = Field(..., description="Outcome status: 'success', 'failed', 'dropped'")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Safe structural metadata only.")

class RedactionResult(BaseModel):
    """
    Metrics on what was removed during the sanitization process.
    """
    original_length: int = Field(..., ge=0)
    redacted_length: int = Field(..., ge=0)
    redacted_fields: List[str] = Field(default_factory=list, description="List of JSON keys that were scrubbed.")
    is_successful: bool = Field(..., description="Must be True if sanitization completed without exception.")

class SanitizedFinding(BaseModel):
    """
    The canonical data structure for a vulnerability finding AFTER it has passed
    through the ABLATION engine. This is the only object allowed to reach the UI or DB.
    """
    model_config = ConfigDict(strict=True)

    finding_id: str = Field(..., description="Unique UUID for the finding")
    scanner_name: str = Field(..., description="The TOKAMAK agent that found this")
    severity: str = Field(..., pattern="^(INFO|LOW|MEDIUM|HIGH|CRITICAL)$")

    # The actual payload, guaranteed to be stripped of credentials
    sanitized_payload: Dict[str, Any]

    # Audit trail of the redaction process
    redaction_metrics: RedactionResult

    # The Fail-Closed Gatekeeper
    is_sanitized: bool = Field(
        default=False,
        description="CRITICAL: Defaults to False. Must be explicitly flipped by the Redactor."
    )