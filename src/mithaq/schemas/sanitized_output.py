"""SanitizedOutput Pydantic schema for sanitization results."""

from typing import List

from pydantic import BaseModel, ConfigDict, field_validator


class SanitizedOutput(BaseModel):
    """Output from sanitization process with detected secrets and sanitized text.

    Ensures consistency between sanitization_applied flag and actual changes.
    """

    model_config = ConfigDict(extra="forbid")

    original_text: str
    sanitized_text: str
    secrets_found: List[str]
    sanitization_applied: bool

    @field_validator("sanitization_applied")
    @classmethod
    def validate_consistency(cls, value: bool, info) -> bool:
        """Ensure sanitization_applied matches actual text changes.

        Args:
            value: The sanitization_applied flag
            info: Validation context containing other fields

        Returns:
            The validated boolean value

        Raises:
            ValueError: If flag doesn't match reality
        """
        data = info.data

        # Get original and sanitized text from context
        original = data.get("original_text", "")
        sanitized = data.get("sanitized_text", "")
        secrets = data.get("secrets_found", [])

        # Check consistency
        text_changed = original != sanitized
        has_secrets = len(secrets) > 0

        # If sanitization_applied is True, text must have changed
        if value is True and not text_changed:
            raise ValueError(
                "sanitization_applied is True but text unchanged. "
                "Flag must match actual sanitization."
            )

        # If sanitization_applied is False, text must be unchanged
        if value is False and text_changed:
            raise ValueError(
                "sanitization_applied is False but text was modified. "
                "Flag must match actual sanitization."
            )

        # If secrets found, sanitization must be applied
        if has_secrets and not value:
            raise ValueError(
                f"Found {len(secrets)} secret(s) but sanitization_applied is False. "
                "Must sanitize when secrets detected."
            )

        return value
