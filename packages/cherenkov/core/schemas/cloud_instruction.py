"""Pydantic schema for cloud-based security instructions."""

import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class CloudInstruction(BaseModel):
    """Instruction for cloud-based security testing agents."""

    task_id: str = Field(..., description="Unique task identifier")
    action: Literal[
        "analyze_smali",
        "web_recon",
        "validate_cve",
        "complete_audit",
        "analyze_threat_model",
        "design_architecture",
    ] = Field(..., description="Action to perform")
    target: str = Field(..., description="Target of the action (e.g., file, URL, CVE-ID)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")
    reasoning: str = Field(..., description="Reasoning behind the action")

    @field_validator("target")
    @classmethod
    def validate_target_no_secrets(cls, v: str) -> str:
        """Ensure target doesn't contain secrets."""
        aws_pattern = r"AKIA[0-9A-Z]{16}"
        jwt_pattern = r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"

        if re.search(aws_pattern, v):
            raise ValueError(
                "AWS access key detected in target. Remove secrets before creating instruction."
            )

        if re.search(jwt_pattern, v):
            raise ValueError(
                "JWT token detected in target. Remove secrets before creating instruction."
            )

        return v

    @field_validator("reasoning")
    @classmethod
    def validate_reasoning_no_secrets(cls, v: str) -> str:
        """Ensure reasoning doesn't contain secrets or prompt injections."""
        aws_pattern = r"AKIA[0-9A-Z]{16}"
        jwt_pattern = r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"

        # More specific prompt injection patterns (avoid false positives)
        prompt_injection_patterns = [
            r"(?i)ignore\s+previous\s+instructions",
            r"(?i)forget\s+previous",
            r"(?i)disregard\s+previous",
            r"(?i)new\s+instructions:",
        ]

        if re.search(aws_pattern, v):
            raise ValueError(
                f"AWS access key detected in reasoning: '{v[:50]}...'. "
                "Use Sanitizer to clean input before creating instruction."
            )

        if re.search(jwt_pattern, v):
            raise ValueError(
                "JWT token detected in reasoning. "
                "Use Sanitizer to clean input before creating instruction."
            )

        for pattern in prompt_injection_patterns:
            if re.search(pattern, v):
                match = re.search(pattern, v)
                raise ValueError(
                    f"Prompt injection detected in reasoning: '{match.group()}'. "
                    "Instruction rejected for security."
                )

        return v

    model_config = {"extra": "forbid"}
