# src/mithaq/agents/burhan.py
"""
Al-Burhan (البرهان) — Proof validation agent.

CHANGE FROM V3: Binary pass/fail replaced with PoC Confidence Score.
(Accepted: Gemini + Copilot — env mismatch causes real vulns to be discarded)

PoC Confidence levels:
  CONFIRMED  — PoC executed, evidence produced, SHA-256 signed → Burhan stamp
  PROBABLE   — PoC partial or env mismatch → routed to human review queue
  UNVERIFIED — Cannot attempt PoC (wrong surface, missing tool) → labeled as such
  DISCARDED  — PoC failed definitively (not env issue) → removed from report

CHANGE FROM V3: Watchdog timer kills stalled PoC containers.
(Accepted: Arch review — hanging exploits freeze worker nodes)
"""
from __future__ import annotations

import asyncio
import hashlib
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.base_scanner import Finding

logger = logging.getLogger("mithaq.burhan")

# Hard limits
POC_TIMEOUT_SECONDS       = 30    # Kill stalled PoC containers
POC_MAX_RETRIES           = 2     # Retry on env mismatch before PROBABLE
WATCHDOG_CHECK_INTERVAL   = 0.5   # Poll interval for watchdog


class BurhanVerdict(str, Enum):
    CONFIRMED  = "confirmed"   # PoC succeeded → Burhan stamp
    PROBABLE   = "probable"    # Env mismatch or partial → human review
    UNVERIFIED = "unverified"  # Cannot attempt PoC on this surface
    DISCARDED  = "discarded"   # PoC failed definitively


@dataclass
class BurhanTrace:
    """
    The MITHAQ Trace artifact. SHA-256 signed forensic log.
    Every CONFIRMED or PROBABLE finding generates one.
    """
    finding_title:     str
    verdict:           BurhanVerdict
    poc_technique:     str
    evidence_summary:  str                     # Sanitized — safe to transmit
    sha256_evidence:   str                     # Hash of raw evidence — local only
    agent_attribution: str = "Al-Burhan"
    timestamp:         float = field(default_factory=time.time)
    duration_ms:       float = 0.0
    human_review_required: bool = False
    confidence_notes:  str = ""

    def sign(self) -> str:
        """Produce a SHA-256 signature over the trace content."""
        payload = (
            f"{self.finding_title}|{self.verdict}|"
            f"{self.poc_technique}|{self.sha256_evidence}|"
            f"{self.timestamp}"
        )
        return hashlib.sha256(payload.encode()).hexdigest()


@dataclass
class BurhanResult:
    finding_title: str
    verdict:       BurhanVerdict
    trace:         BurhanTrace | None
    signature:     str | None = None


# ──────────────────────────────────────────────
# PoC Primitive library (Phase 2 deliverable)
# ──────────────────────────────────────────────

class PoCPrimitive:
    """
    Safe, non-destructive PoC techniques.
    Every technique must be read-only or leave no persistent side effect.
    """
    PRIMITIVES: dict[str, str] = {
        # SQL injection: read-only probe
        "sql_injection":      "SELECT 1 FROM dual WHERE 1=1",
        # XSS: non-executing sentinel
        "xss_reflected":      "<mithaq-probe-xss>",
        # SSRF: probe internal DNS, not fetch content
        "ssrf_basic":         "http://metadata.probe.mithaq.internal/",
        # Auth bypass: empty credential probe
        "auth_bypass":        "' OR '1'='1' --",
        # JWT: alg=none probe (read-only)
        "jwt_none_alg":       '{"alg":"none","typ":"JWT"}',
        # Path traversal: read /etc/hostname only
        "path_traversal":     "../../../../etc/hostname",
        # Header injection: CRLF probe
        "header_injection":   "%0d%0aX-mithaq-Probe: 1",
        # Command injection: echo only
        "command_injection":  ";echo mithaq-burhan-probe",
        # XXE: external entity to controlled host
        "xxe_basic":          '<!DOCTYPE foo [<!ENTITY ext SYSTEM "http://probe.mithaq.internal">]>',
        # IDOR: increment resource ID by 1
        "idor_basic":         "resource_id + 1",
        # Open redirect: redirect to controlled domain
        "open_redirect":      "https://probe.mithaq.internal/callback",
    }

    @classmethod
    def get(cls, technique: str) -> str | None:
        return cls.PRIMITIVES.get(technique)

    @classmethod
    def is_safe(cls, technique: str) -> bool:
        """Check if a technique is in the approved primitive library."""
        return technique in cls.PRIMITIVES


# ──────────────────────────────────────────────
# The validation agent
# ──────────────────────────────────────────────

class BurhanAgent:
    """
    Validates every HIGH/CRITICAL finding before it reaches the report.

    Execution flow:
      1. Check if a safe PoC primitive exists for this finding type
      2. Execute PoC in ephemeral sandbox with watchdog timer
      3. Assign confidence score: CONFIRMED / PROBABLE / UNVERIFIED / DISCARDED
      4. Generate mithaq Trace with SHA-256 signature
    """

    def __init__(
        self,
        sandbox_executor=None,           # injected in production
        timeout: int = POC_TIMEOUT_SECONDS,
    ) -> None:
        self.sandbox = sandbox_executor
        self.timeout = timeout

    async def validate(self, finding: "Finding", target: str) -> BurhanResult:
        """
        Validate a finding. Routes to appropriate technique based on scanner name.
        """
        t0 = time.monotonic()
        technique = finding.scanner

        # Check if we have a safe primitive for this finding type
        if not PoCPrimitive.is_safe(technique):
            return BurhanResult(
                finding_title=finding.title,
                verdict=BurhanVerdict.UNVERIFIED,
                trace=self._make_trace(
                    finding, BurhanVerdict.UNVERIFIED, technique, t0,
                    confidence_notes=f"No safe PoC primitive for scanner '{technique}'"
                ),
            )

        payload = PoCPrimitive.get(technique)
        retries = 0

        while retries <= POC_MAX_RETRIES:
            try:
                result = await asyncio.wait_for(
                    self._execute_poc(target, technique, payload),
                    timeout=self.timeout,
                )

                if result["exploitable"]:
                    trace = self._make_trace(
                        finding, BurhanVerdict.CONFIRMED, technique, t0,
                        evidence=result.get("evidence", ""),
                        confidence_notes="PoC executed successfully"
                    )
                    signature = trace.sign()
                    logger.info("MITHAQ Trace generated and signed for finding: %s", finding.title)
                    return BurhanResult(
                        finding_title=finding.title,
                        verdict=BurhanVerdict.CONFIRMED,
                        trace=trace,
                        signature=signature,
                    )

                # Not exploitable — discard
                trace = self._make_trace(
                    finding, BurhanVerdict.DISCARDED, technique, t0,
                    confidence_notes="PoC executed but finding not reproducible"
                )
                return BurhanResult(
                    finding_title=finding.title,
                    verdict=BurhanVerdict.DISCARDED,
                    trace=trace,
                )

            except asyncio.TimeoutError:
                retries += 1
                logger.warning(
                    "Burhan PoC timed out for '%s' on '%s' (attempt %d/%d). "
                    "Watchdog killed stalled container.",
                    technique, target, retries, POC_MAX_RETRIES + 1
                )
                await self._kill_stalled_container()

            except EnvironmentError as e:
                # Environment mismatch (missing tool, wrong OS, etc.)
                retries += 1
                logger.info("Burhan env mismatch: %s (attempt %d)", e, retries)

        # Exceeded retries — PROBABLE (env issue, not definitively safe)
        trace = self._make_trace(
            finding, BurhanVerdict.PROBABLE, technique, t0,
            confidence_notes=(
                f"PoC failed {POC_MAX_RETRIES + 1}x due to timeouts or "
                "environment mismatch. Human review required."
            ),
        )
        trace.human_review_required = True
        return BurhanResult(
            finding_title=finding.title,
            verdict=BurhanVerdict.PROBABLE,
            trace=trace,
        )

    async def _execute_poc(
        self, target: str, technique: str, payload: str
    ) -> dict:
        """
        Execute PoC in ephemeral sandbox container.
        In production: delegates to ScanSandbox.
        In tests: sandbox is mocked.
        """
        if self.sandbox is None:
            raise EnvironmentError("No sandbox executor configured")
        return await self.sandbox.run_poc(target, technique, payload)

    async def _kill_stalled_container(self) -> None:
        """
        Watchdog: kill stalled PoC container and free memory.
        Prevents a hung exploit from freezing worker nodes.
        (Accepted: Arch review)
        """
        if self.sandbox:
            try:
                await self.sandbox.kill_active()
            except Exception as e:
                logger.warning("Watchdog kill failed: %s", e)

    def _make_trace(
        self,
        finding: "Finding",
        verdict: BurhanVerdict,
        technique: str,
        t0: float,
        evidence: str = "",
        confidence_notes: str = "",
    ) -> BurhanTrace:
        raw_evidence = (
            f"{finding.title}|{technique}|{evidence}"
        )
        sha256 = hashlib.sha256(raw_evidence.encode()).hexdigest()
        return BurhanTrace(
            finding_title=finding.title,
            verdict=verdict,
            poc_technique=technique,
            evidence_summary=f"[{verdict.value.upper()}] {technique}",
            sha256_evidence=sha256,
            duration_ms=(time.monotonic() - t0) * 1000,
            human_review_required=(verdict == BurhanVerdict.PROBABLE),
            confidence_notes=confidence_notes,
        )

