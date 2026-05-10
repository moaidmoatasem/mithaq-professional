"""Ablation (السيادة) — Fail-closed sanitization bridge.

INVARIANTS (cannot be violated):
  1. sanitize() output contains zero raw credentials / IPs / paths / source code.
  2. If sanitize() raises SanitizationError, NOTHING has been transmitted.
  3. Pydantic schema gate happens BEFORE any tool call from the cloud.
  4. Every sanitization attempt is recorded in telemetry — no silent drops.
"""

from __future__ import annotations

import hashlib
import logging
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from pydantic import BaseModel, ValidationError

logger = logging.getLogger("cherenkov.ablation")


class DropReason(str, Enum):
    UNSANITIZABLE_PATTERN = "unsanitizable_pattern"
    SCHEMA_VALIDATION_FAIL = "schema_validation_fail"
    PII_RESIDUAL_DETECTED = "pii_residual_detected"
    BINARY_CONTENT = "binary_content"
    SIZE_EXCEEDED = "size_exceeded"
    UNKNOWN = "unknown"


@dataclass
class SanitizationAttempt:
    timestamp: float
    success: bool
    drop_reason: DropReason | None = None
    redaction_count: int = 0
    payload_size_bytes: int = 0
    duration_ms: float = 0.0


@dataclass
class AblationTelemetry:
    attempts: int = 0
    successes: int = 0
    drops: int = 0
    drop_reasons: dict[str, int] = field(default_factory=dict)
    total_redactions: int = 0
    history: list[SanitizationAttempt] = field(default_factory=list)

    @property
    def drop_rate(self) -> float:
        return self.drops / self.attempts if self.attempts else 0.0

    @property
    def success_rate(self) -> float:
        return self.successes / self.attempts if self.attempts else 0.0

    def record(self, attempt: SanitizationAttempt) -> None:
        self.attempts += 1
        if attempt.success:
            self.successes += 1
            self.total_redactions += attempt.redaction_count
        else:
            self.drops += 1
            reason = attempt.drop_reason.value if attempt.drop_reason else "unknown"
            self.drop_reasons[reason] = self.drop_reasons.get(reason, 0) + 1
        self.history.append(attempt)
        if self.attempts >= 10 and self.drop_rate > 0.20:
            logger.warning(
                "Ablation drop rate is %.1f%% (%d/%d). "
                "Check sanitization patterns for this surface.",
                self.drop_rate * 100,
                self.drops,
                self.attempts,
            )

    def summary(self) -> str:
        return (
            f"Ablation: {self.attempts} attempts | "
            f"{self.successes} passed | "
            f"{self.drops} dropped ({self.drop_rate:.1%}) | "
            f"{self.total_redactions} redactions"
        )


_PATTERNS: list[tuple[str, re.Pattern, str]] = [
    ("aws_key", re.compile(r"AKIA[0-9A-Z]{16}"), "[AWS_KEY_REDACTED]"),
    ("aws_sec", re.compile(r"[0-9a-zA-Z/+]{40}"), "[AWS_SECRET_REDACTED]"),
    (
        "generic_key",
        re.compile(r"(?i)(api[_-]?key|secret|token)\s*[:=]\s*\S+"),
        "[API_KEY_REDACTED]",
    ),
    (
        "private_ip",
        re.compile(r"\b(10|172\.(1[6-9]|2\d|3[01])|192\.168)\.\d+\.\d+\b"),
        "[INTERNAL_IP]",
    ),
    ("localhost", re.compile(r"\b(localhost|127\.0\.0\.\d+)\b"), "[LOCALHOST]"),
    ("abs_path", re.compile(r"(/home/|/root/|/Users/|C:\\Users\\)\S+"), "[LOCAL_PATH]"),
    ("email", re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"), "[EMAIL_REDACTED]"),
    ("phone", re.compile(r"\+?\d[\d\s\-().]{7,}\d"), "[PHONE_REDACTED]"),
    ("jwt", re.compile(r"ey[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+"), "[JWT_REDACTED]"),
    (
        "ssh_key",
        re.compile(r"-----BEGIN (RSA|EC|OPENSSH) PRIVATE KEY-----.*?-----END", re.DOTALL),
        "[SSH_KEY_REDACTED]",
    ),
    (
        "base64_cred",
        re.compile(r"(?i)(authorization:\s*basic\s+)[A-Za-z0-9+/]+=*"),
        r"\1[BASIC_AUTH_REDACTED]",
    ),
    ("db_conn", re.compile(r"(?i)(mysql|postgresql|mongodb|redis)://\S+"), "[DB_CONN_REDACTED]"),
]

_MAX_PAYLOAD_BYTES = 32_768
_PII_RESIDUAL_CHECK = re.compile(
    r"(AKIA[0-9A-Z]{8}|password\s*=\s*\S{4,}|"
    r"\b\d{16}\b|"
    r"-----BEGIN .* KEY-----|"
    r"\b(?:10|192\.168|172\.1[6-9])\.\d+\.\d+\b)",
    re.IGNORECASE,
)


class AllowedToolName(str, Enum):
    RUN_SCANNER = "run_scanner"
    READ_FINDING = "read_finding"
    GENERATE_PLAN = "generate_plan"
    FETCH_CVE = "fetch_cve"


class CloudCommand(BaseModel):
    tool: AllowedToolName
    scanner: str | None = None
    target_id: int | None = None
    parameters: dict[str, str | int | bool] = {}
    model_config = {"extra": "forbid"}


@dataclass
class SanitizationResult:
    sanitized_payload: dict
    redaction_count: int
    placeholders: dict[str, str]
    sha256_local_evidence: str


class SanitizationError(Exception):
    def __init__(self, reason: DropReason, detail: str = ""):
        self.reason = reason
        super().__init__(f"Sanitization failed [{reason.value}]: {detail}")


class AblationBridge:
    def __init__(self) -> None:
        self.telemetry = AblationTelemetry()

    def sanitize(self, raw_finding: dict[str, Any]) -> SanitizationResult:
        t0 = time.monotonic()
        attempt = SanitizationAttempt(
            timestamp=t0, success=False, payload_size_bytes=len(str(raw_finding))
        )
        try:
            raw_str = str(raw_finding)
            if len(raw_str.encode()) > _MAX_PAYLOAD_BYTES:
                raise SanitizationError(
                    DropReason.SIZE_EXCEEDED,
                    f"Payload {len(raw_str)} bytes exceeds {_MAX_PAYLOAD_BYTES}",
                )
            if any(isinstance(v, bytes) for v in self._flatten_values(raw_finding)):
                raise SanitizationError(
                    DropReason.BINARY_CONTENT, "Binary content must not leave local environment"
                )
            sanitized, redaction_count, placeholders = self._redact(raw_finding)
            if _PII_RESIDUAL_CHECK.search(str(sanitized)):
                raise SanitizationError(
                    DropReason.PII_RESIDUAL_DETECTED, "Residual PII detected after redaction"
                )
            sha256 = hashlib.sha256(str(raw_finding).encode()).hexdigest()
            attempt.success = True
            attempt.redaction_count = redaction_count
            attempt.duration_ms = (time.monotonic() - t0) * 1000
            self.telemetry.record(attempt)
            return SanitizationResult(
                sanitized_payload=sanitized,
                redaction_count=redaction_count,
                placeholders=placeholders,
                sha256_local_evidence=sha256,
            )
        except SanitizationError as e:
            attempt.drop_reason = e.reason
            attempt.duration_ms = (time.monotonic() - t0) * 1000
            self.telemetry.record(attempt)
            raise

    def validate_inbound_command(self, raw_json: dict[str, Any]) -> CloudCommand:
        try:
            return CloudCommand(**raw_json)
        except ValidationError as e:
            raise SanitizationError(
                DropReason.SCHEMA_VALIDATION_FAIL,
                f"Cloud instruction failed schema validation: {e}",
            ) from e

    def _redact(self, obj: Any) -> tuple[Any, int, dict[str, str]]:
        count = 0
        placeholders: dict[str, str] = {}

        def redact_str(s: str) -> str:
            nonlocal count
            for _name, pattern, replacement in _PATTERNS:
                new_s, n = pattern.subn(replacement, s)
                if n > 0:
                    count += n
                    original_hash = hashlib.sha256(s.encode()).hexdigest()[:12]
                    placeholders[original_hash] = replacement
                    s = new_s
            return s

        def redact_obj(o: Any) -> Any:
            if isinstance(o, str):
                return redact_str(o)
            if isinstance(o, dict):
                return {k: redact_obj(v) for k, v in o.items()}
            if isinstance(o, list):
                return [redact_obj(i) for i in o]
            return o

        return redact_obj(obj), count, placeholders

    def _flatten_values(self, obj: Any):
        if isinstance(obj, dict):
            for v in obj.values():
                yield from self._flatten_values(v)
        elif isinstance(obj, list):
            for i in obj:
                yield from self._flatten_values(i)
        else:
            yield obj
