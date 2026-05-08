"""Sanitizer for detecting and redacting sensitive information."""

import re

from cherenkov.schemas.sanitized_output import SanitizedOutput


class Sanitizer:
    """Detects and sanitizes sensitive information from text.

    Supports detection of:
    - AWS access keys (AKIA...)
    - JWT tokens (eyJ...)
    - Prompt injection attempts
    """

    # Regex patterns for secret detection
    AWS_KEY_PATTERN = re.compile(r"AKIA[A-Z0-9]{16}")
    JWT_PATTERN = re.compile(r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+")
    PROMPT_INJECTION_PATTERN = re.compile(
        r"\b(ignore previous|new instructions|disregard|forget everything)\b",
        re.IGNORECASE,
    )

    def sanitize(self, text: str) -> SanitizedOutput:
        """Sanitize text by detecting and redacting secrets.

        Args:
            text: The text to sanitize

        Returns:
            SanitizedOutput with detected secrets and sanitized text
        """
        if not text:
            return SanitizedOutput(
                original_text=text,
                sanitized_text=text,
                secrets_found=[],
                sanitization_applied=False,
            )

        secrets_found = []
        sanitized_text = text

        # Detect and redact AWS keys
        aws_matches = self.AWS_KEY_PATTERN.findall(text)
        for match in aws_matches:
            secrets_found.append(f"AWS_KEY:{match}")
            sanitized_text = sanitized_text.replace(match, "[REDACTED]")

        # Detect and redact JWT tokens
        jwt_matches = self.JWT_PATTERN.findall(text)
        for match in jwt_matches:
            secrets_found.append(f"JWT:{match}")
            sanitized_text = sanitized_text.replace(match, "[REDACTED]")

        # Detect and redact prompt injections
        injection_matches = self.PROMPT_INJECTION_PATTERN.findall(text)
        for match in injection_matches:
            secrets_found.append(f"PROMPT_INJECTION:{match}")
            sanitized_text = self.PROMPT_INJECTION_PATTERN.sub(
                "[REDACTED]", sanitized_text
            )

        sanitization_applied = len(secrets_found) > 0

        return SanitizedOutput(
            original_text=text,
            sanitized_text=sanitized_text,
            secrets_found=secrets_found,
            sanitization_applied=sanitization_applied,
        )

