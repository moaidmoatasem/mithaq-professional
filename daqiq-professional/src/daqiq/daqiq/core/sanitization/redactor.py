"""
Data Redaction Layer - Fail-Closed Sanitization
Ensures sensitive data never reaches cloud agents.
"""

import re
import hashlib
from typing import Dict, Any, Optional, List, Tuple
from pydantic import BaseModel, Field
from enum import Enum


class RedactionLevel(Enum):
    """Levels of data redaction"""

    MINIMAL = "minimal"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class RedactionResult(BaseModel):
    """Result of redaction operation"""

    sanitized_data: Dict[str, Any]
    redacted_fields: List[str]
    hash_signature: str
    is_safe: bool
    warnings: List[str] = Field(default_factory=list)


class DataRedactor:
    """
    Fail-closed data sanitization for cloud transmission.
    """

    PATTERNS = {
        "api_key": re.compile(
            r'(?i)(api[_-]?key|apikey|token)\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?'
        ),
        "password": re.compile(
            r'(?i)(password|passwd|pwd)\s*[:=]\s*["\']?([^\s"\']+)["\']?'
        ),
        "secret": re.compile(
            r'(?i)(secret|private[_-]?key)\s*[:=]\s*["\']?([a-zA-Z0-9_\-+/=]{20,})["\']?'
        ),
        "aws_key": re.compile(r"AKIA[0-9A-Z]{16}"),
        "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
        "ip_address": re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"),
        "jwt": re.compile(r"eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*"),
        "db_connection": re.compile(r"(?i)(mongodb|mysql|postgresql)://[^\s]+"),
        "file_path": re.compile(r"(/home/[^\s]+|C:\\[^\s]+|/var/[^\s]+)"),
    }

    def __init__(self, level: RedactionLevel = RedactionLevel.MODERATE):
        self.level = level
        self.redaction_count = 0

    def redact_text(self, text: str) -> Tuple[str, List[str]]:
        """Redact sensitive information from text."""
        redacted_types = []

        for secret_type, pattern in self.PATTERNS.items():
            if pattern.search(text):
                text = pattern.sub(f"[{secret_type.upper()}_REDACTED]", text)
                redacted_types.append(secret_type)
                self.redaction_count += 1

        return text, redacted_types

    def _is_sensitive_key(self, key: str) -> bool:
        """Check if dictionary key suggests sensitive data"""
        sensitive_keywords = [
            "password",
            "secret",
            "token",
            "key",
            "auth",
            "credential",
            "apikey",
            "private",
            "jwt",
        ]
        return any(keyword in key.lower() for keyword in sensitive_keywords)

    def _generate_hash(self, data: Dict[str, Any]) -> str:
        """Generate SHA-256 hash of original data"""
        data_str = str(sorted(data.items()))
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]

    def _validate_safety(self, sanitized: Dict[str, Any]) -> bool:
        """Validate sanitized data is safe for cloud"""
        data_str = str(sanitized)

        for pattern in self.PATTERNS.values():
            if pattern.search(data_str):
                return False

        return True

    def redact_dict(self, data: Dict[str, Any]) -> RedactionResult:
        """Redact sensitive data from dictionary."""
        sanitized = {}
        redacted_fields = []
        warnings = []

        for key, value in data.items():
            if self._is_sensitive_key(key):
                sanitized[key] = "[REDACTED]"
                redacted_fields.append(key)
                continue

            if isinstance(value, str):
                redacted_value, types = self.redact_text(value)
                sanitized[key] = redacted_value
                if types:
                    redacted_fields.extend(types)

            elif isinstance(value, dict):
                nested_result = self.redact_dict(value)
                sanitized[key] = nested_result.sanitized_data
                redacted_fields.extend(nested_result.redacted_fields)
                warnings.extend(nested_result.warnings)

            elif isinstance(value, list):
                sanitized[key] = [
                    self.redact_text(item)[0] if isinstance(item, str) else item
                    for item in value
                ]

            else:
                sanitized[key] = value

        hash_sig = self._generate_hash(data)
        is_safe = self._validate_safety(sanitized)

        if not is_safe:
            warnings.append("FAIL_CLOSED: Unsanitizable data detected.")

        return RedactionResult(
            sanitized_data=sanitized,
            redacted_fields=list(set(redacted_fields)),
            hash_signature=hash_sig,
            is_safe=is_safe,
            warnings=warnings,
        )

    def create_breadcrumb(
        self, original_data: Dict[str, Any], metadata_only: bool = True
    ) -> Dict[str, Any]:
        """Create abstract breadcrumb for cloud agent."""
        if metadata_only:
            return {
                "data_type": type(original_data).__name__,
                "field_count": len(original_data),
                "field_names": list(original_data.keys()),
                "has_nested": any(isinstance(v, dict) for v in original_data.values()),
                "timestamp": "REDACTED",
                "source": "LOCAL_EXECUTOR",
            }

        result = self.redact_dict(original_data)
        if not result.is_safe:
            raise ValueError("FAIL_CLOSED: Cannot create safe breadcrumb")

        return result.sanitized_data
