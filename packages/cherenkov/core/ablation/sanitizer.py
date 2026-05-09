"""
Sanitizers for detecting and redacting sensitive information.
"""

import hashlib
import hmac
import json
import re
from typing import Any, Dict

from pydantic import BaseModel

from cherenkov.core.ablation.redactor import DataRedactor, RedactionLevel, RedactionResult
from cherenkov.core.schemas.sanitized_output import SanitizedOutput


class SanitizedPayload(BaseModel):
    """Payload containing sanitized data and its HMAC signature."""

    sanitized_data: Dict[str, Any]
    hmac_signature: str
    original_hash: str
    is_safe: bool


class Sanitizer:
    """Detects and sanitizes sensitive information from text.

    Supports detection of:
    - AWS access keys (AKIA...)
    - JWT tokens (eyJ...)
    - Prompt injection attempts
    """

    AWS_KEY_PATTERN = re.compile(r"AKIA[A-Z0-9]{16}")
    JWT_PATTERN = re.compile(r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+")
    PROMPT_INJECTION_PATTERN = re.compile(
        r"\b(ignore previous|new instructions|disregard|forget everything)\b",
        re.IGNORECASE,
    )

    def sanitize(self, text: str) -> SanitizedOutput:
        """Sanitize text by detecting and redacting secrets."""
        if not text:
            return SanitizedOutput(
                original_text=text,
                sanitized_text=text,
                secrets_found=[],
                sanitization_applied=False,
            )

        secrets_found = []
        sanitized_text = text

        aws_matches = self.AWS_KEY_PATTERN.findall(text)
        for match in aws_matches:
            secrets_found.append(f"AWS_KEY:{match}")
            sanitized_text = sanitized_text.replace(match, "[REDACTED]")

        jwt_matches = self.JWT_PATTERN.findall(text)
        for match in jwt_matches:
            secrets_found.append(f"JWT:{match}")
            sanitized_text = sanitized_text.replace(match, "[REDACTED]")

        injection_matches = self.PROMPT_INJECTION_PATTERN.findall(text)
        for match in injection_matches:
            secrets_found.append(f"PROMPT_INJECTION:{match}")
            sanitized_text = self.PROMPT_INJECTION_PATTERN.sub("[REDACTED]", sanitized_text)

        sanitization_applied = len(secrets_found) > 0

        return SanitizedOutput(
            original_text=text,
            sanitized_text=sanitized_text,
            secrets_found=secrets_found,
            sanitization_applied=sanitization_applied,
        )


class AblationSanitizer:
    """
    Sanitizes data and signs it with an HMAC to prove it was processed
    by the authorized ablation engine.
    """

    def __init__(self, secret_key: bytes, level: RedactionLevel = RedactionLevel.MODERATE):
        """
        Initialize the sanitizer with a secret key for HMAC signing.
        """
        if not secret_key:
            raise ValueError("Secret key is required for AblationSanitizer")

        self.secret_key = secret_key
        self.redactor = DataRedactor(level=level)

    def _generate_hmac(self, data: Dict[str, Any]) -> str:
        """
        Generate HMAC-SHA256 signature for the dictionary data.
        Data is sorted by key to ensure consistent JSON serialization.
        """
        # Sort keys to ensure deterministic serialization
        serialized_data = json.dumps(data, sort_keys=True).encode("utf-8")
        signature = hmac.new(self.secret_key, serialized_data, hashlib.sha256).hexdigest()
        return signature

    def sanitize_and_sign(self, data: Dict[str, Any]) -> SanitizedPayload:
        """
        Sanitize the dictionary and return it along with an HMAC signature.
        """
        redaction_result: RedactionResult = self.redactor.redact_dict(data)

        # If it's not safe, we shouldn't sign it as safe data
        if not redaction_result.is_safe:
            raise ValueError("FAIL_CLOSED: Data could not be safely sanitized.")

        hmac_sig = self._generate_hmac(redaction_result.sanitized_data)

        return SanitizedPayload(
            sanitized_data=redaction_result.sanitized_data,
            hmac_signature=hmac_sig,
            original_hash=redaction_result.hash_signature,
            is_safe=redaction_result.is_safe,
        )

    def verify_signature(self, payload: SanitizedPayload) -> bool:
        """
        Verify that the HMAC signature matches the sanitized data.
        Uses timing-safe comparison to prevent timing attacks.
        """
        expected_sig = self._generate_hmac(payload.sanitized_data)
        return hmac.compare_digest(payload.hmac_signature, expected_sig)
