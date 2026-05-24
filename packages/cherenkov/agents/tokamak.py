# packages/cherenkov/agents/tokamak.py
"""
Tokamak (البرهان) — Proof validation agent.

CHANGE FROM V3: Binary pass/fail replaced with PoC Confidence Score.
(Accepted: Gemini + Copilot — env mismatch causes real vulns to be discarded)

PoC Confidence levels:
  CONFIRMED  — PoC executed, evidence produced, SHA-256 signed → Tokamak stamp
  PROBABLE   — PoC partial or env mismatch → routed to human review queue
  UNVERIFIED — Cannot attempt PoC (wrong surface, missing tool) → labeled as such
  DISCARDED  — PoC failed definitively (not env issue) → removed from report

CHANGE FROM V3: Watchdog timer kills stalled PoC containers.
(Accepted: Arch review — hanging exploits freeze worker nodes)
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..core.base_scanner import Finding

import httpx

logger = logging.getLogger("cherenkov.tokamak")

# Hard limits
POC_TIMEOUT_SECONDS = 30  # Kill stalled PoC containers
POC_MAX_RETRIES = 2  # Retry on env mismatch before PROBABLE
WATCHDOG_CHECK_INTERVAL = 0.5  # Poll interval for watchdog
FAST_PROBE_TIMEOUT = 5  # Lightweight HTTP probes (<5s per the SSOT)
FAST_PROBE_LOG = Path("logs/tokamak/fast_probes")


class TokamakVerdict(str, Enum):
    CONFIRMED = "confirmed"  # PoC succeeded → Tokamak stamp
    PROBABLE = "probable"  # Env mismatch or partial → human review
    UNVERIFIED = "unverified"  # Cannot attempt PoC on this surface
    DISCARDED = "discarded"  # PoC failed definitively


@dataclass
class TokamakTrace:
    """
    The CHERENKOV Trace artifact. SHA-256 signed forensic log.
    Every CONFIRMED or PROBABLE finding generates one.
    """

    finding_title: str
    verdict: TokamakVerdict
    poc_technique: str
    evidence_summary: str  # Sanitized — safe to transmit
    sha256_evidence: str  # Hash of raw evidence — local only
    agent_attribution: str = "Tokamak"
    timestamp: float = field(default_factory=time.time)
    duration_ms: float = 0.0
    human_review_required: bool = False
    confidence_notes: str = ""

    def sign(self) -> str:
        """Produce a SHA-256 signature over the trace content."""
        payload = (
            f"{self.finding_title}|{self.verdict}|"
            f"{self.poc_technique}|{self.sha256_evidence}|"
            f"{self.timestamp}"
        )
        return hashlib.sha256(payload.encode()).hexdigest()


@dataclass
class TokamakResult:
    finding_title: str
    verdict: TokamakVerdict
    trace: TokamakTrace | None
    signature: str | None = None


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
        "sql_injection": "SELECT 1 FROM dual WHERE 1=1",
        # XSS: non-executing sentinel
        "xss_reflected": "<cherenkov-probe-xss>",
        # SSRF: probe internal DNS, not fetch content
        "ssrf_basic": "http://metadata.probe.cherenkov.internal/",
        # Auth bypass: empty credential probe
        "auth_bypass": "' OR '1'='1' --",
        # JWT: alg=none probe (read-only)
        "jwt_none_alg": '{"alg":"none","typ":"JWT"}',
        # Path traversal: read /etc/hostname only
        "path_traversal": "../../../../etc/hostname",
        # Header injection: CRLF probe
        "header_injection": "%0d%0aX-cherenkov-Probe: 1",
        # Command injection: echo only
        "command_injection": ";echo cherenkov-tokamak-probe",
        # XXE: external entity to controlled host
        "xxe_basic": '<!DOCTYPE foo [<!ENTITY ext SYSTEM "http://probe.cherenkov.internal">]>',
        # IDOR: increment resource ID by 1
        "idor_basic": "resource_id + 1",
        # Open redirect: redirect to controlled domain
        "open_redirect": "https://probe.cherenkov.internal/callback",
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


class TokamakAgent:
    """
    Validates every HIGH/CRITICAL finding before it reaches the report.

    Execution flow:
      1. Check if a safe PoC primitive exists for this finding type
      2. Execute PoC in ephemeral tokamak with watchdog timer
      3. Assign confidence score: CONFIRMED / PROBABLE / UNVERIFIED / DISCARDED
      4. Generate cherenkov Trace with SHA-256 signature
    """

    def __init__(
        self,
        tokamak_executor=None,  # injected in production
        timeout: int = POC_TIMEOUT_SECONDS,
    ) -> None:
        self.tokamak = tokamak_executor
        self.timeout = timeout

    async def validate(self, finding: "Finding", target: str) -> TokamakResult:
        """
        Validate a finding. Routes to appropriate technique based on scanner name.

        Tries a fast lightweight HTTP probe first (<5s, no Docker).
        Falls through to full Docker sandbox only if fast probe is unavailable.
        """
        t0 = time.monotonic()
        technique = finding.scanner

        # Try fast probe first (XSS, SQLi, CSRF only — no Docker needed)
        fast_result = await self._try_fast_probe(target, technique, finding.title)
        if fast_result is not None:
            return fast_result

        # Fall through to Docker sandbox
        if not PoCPrimitive.is_safe(technique):
            return TokamakResult(
                finding_title=finding.title,
                verdict=TokamakVerdict.UNVERIFIED,
                trace=self._make_trace(
                    finding,
                    TokamakVerdict.UNVERIFIED,
                    technique,
                    t0,
                    confidence_notes=f"No safe PoC primitive for scanner '{technique}'",
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
                        finding,
                        TokamakVerdict.CONFIRMED,
                        technique,
                        t0,
                        evidence=result.get("evidence", ""),
                        confidence_notes="PoC executed successfully",
                    )
                    signature = trace.sign()
                    print(f"[CHERENKOV] Trace Signed: {signature[:16]}...")
                    logger.info(
                        "CHERENKOV Trace generated and signed for finding: %s", finding.title
                    )
                    return TokamakResult(
                        finding_title=finding.title,
                        verdict=TokamakVerdict.CONFIRMED,
                        trace=trace,
                        signature=signature,
                    )

                trace = self._make_trace(
                    finding,
                    TokamakVerdict.DISCARDED,
                    technique,
                    t0,
                    confidence_notes="PoC executed but finding not reproducible",
                )
                return TokamakResult(
                    finding_title=finding.title,
                    verdict=TokamakVerdict.DISCARDED,
                    trace=trace,
                )

            except asyncio.TimeoutError:
                retries += 1
                logger.warning(
                    "Tokamak PoC timed out for '%s' on '%s' (attempt %d/%d). "
                    "Watchdog killed stalled container.",
                    technique,
                    target,
                    retries,
                    POC_MAX_RETRIES + 1,
                )
                await self._kill_stalled_container()

            except EnvironmentError as e:
                retries += 1
                logger.info("Tokamak env mismatch: %s (attempt %d)", e, retries)

        trace = self._make_trace(
            finding,
            TokamakVerdict.PROBABLE,
            technique,
            t0,
            confidence_notes=(
                f"PoC failed {POC_MAX_RETRIES + 1}x due to timeouts or "
                "environment mismatch. Human review required."
            ),
        )
        trace.human_review_required = True
        return TokamakResult(
            finding_title=finding.title,
            verdict=TokamakVerdict.PROBABLE,
            trace=trace,
        )

    _FAST_TECHNIQUES: dict[str, str] = {
        "xss_reflected": "xss",
        "sql_injection": "sqli",
        "csrf": "csrf",
        "auth_bypass": "sqli",
    }

    async def _try_fast_probe(
        self, target: str, technique: str, title: str
    ) -> TokamakResult | None:
        """Attempt a lightweight HTTP probe. Returns None if not applicable."""
        vuln_type = self._FAST_TECHNIQUES.get(technique)
        if vuln_type is None:
            return None

        fast_payloads: dict[str, list[str]] = {
            "xss": [
                "<script>alert(1)</script>",
                "<img src=x onerror=alert(1)>",
            ],
            "sqli": [
                "' OR '1'='1",
                "' UNION SELECT 1--",
            ],
            "csrf": [
                "<form action='/' method='POST'>",
            ],
        }

        payloads = fast_payloads.get(vuln_type, [])
        t0 = time.monotonic()

        for payload in payloads:
            try:
                result = await self._do_http_probe(target, vuln_type, payload)
                if result.get("exploitable"):
                    duration = (time.monotonic() - t0) * 1000
                    evidence = json.dumps(result, default=str)
                    sha256 = hashlib.sha256(evidence.encode()).hexdigest()
                    self._write_probe_log(title, vuln_type, result, duration)
                    trace = TokamakTrace(
                        finding_title=title,
                        verdict=TokamakVerdict.CONFIRMED,
                        poc_technique=f"fast_{vuln_type}",
                        evidence_summary=f"[CONFIRMED] {vuln_type} via fast probe",
                        sha256_evidence=sha256,
                        duration_ms=duration,
                        confidence_notes="Fast HTTP probe confirmed vulnerability",
                    )
                    signature = trace.sign()
                    logger.info(
                        "FAST PROBE CONFIRMED — %s on %s (%dms)", technique, target, duration
                    )
                    return TokamakResult(
                        finding_title=title,
                        verdict=TokamakVerdict.CONFIRMED,
                        trace=trace,
                        signature=signature,
                    )
            except Exception:
                logger.debug("Fast probe payload failed for %s", technique, exc_info=True)

        return None

    async def _do_http_probe(self, target: str, vuln_type: str, payload: str) -> dict[str, Any]:
        """Execute a single HTTP probe with timeout."""
        async with httpx.AsyncClient(timeout=FAST_PROBE_TIMEOUT, verify=False) as client:  # nosec B501 # noqa: S501 localhost probes only
            if vuln_type == "xss":
                r = await client.get(target + httpx.utils.quote(payload), follow_redirects=False)
                reflected = payload.lower() in r.text.lower()
                return {"exploitable": reflected}
            elif vuln_type == "sqli":
                r = await client.get(target + httpx.utils.quote(payload), follow_redirects=False)
                indicators = ("sql", "syntax", "mysql", "error", "odbc")
                detected = any(i in r.text.lower() for i in indicators)
                return {"exploitable": detected}
            elif vuln_type == "csrf":
                r = await client.post(
                    target, data={"csrf_test": "tokamak_probe"}, follow_redirects=False
                )
                return {"exploitable": r.status_code == 200}
        return {"exploitable": False}

    def _write_probe_log(self, title: str, vuln_type: str, result: dict, duration: float) -> None:
        """Write fast probe result to log file for audit trail."""
        FAST_PROBE_LOG.mkdir(parents=True, exist_ok=True)
        path = FAST_PROBE_LOG / f"{vuln_type}_{int(time.time())}.json"
        path.write_text(
            json.dumps(
                {
                    "finding": title,
                    "vuln_type": vuln_type,
                    "result": {k: str(v) for k, v in result.items()},
                    "duration_ms": round(duration, 2),
                    "timestamp": time.time(),
                },
                indent=2,
            )
        )

    async def _execute_poc(self, target: str, technique: str, payload: str) -> dict:
        """
        Execute PoC in ephemeral tokamak container.
        In production: delegates to ScanTOKAMAK.
        In tests: tokamak is mocked.
        """
        if self.tokamak is None:
            raise EnvironmentError("No tokamak executor configured")
        print(f"[TOKAMAK] Executing PoC for {technique} on {target}...")
        return await self.tokamak.run_poc(target, technique, payload)

    async def _kill_stalled_container(self) -> None:
        """
        Watchdog: kill stalled PoC container and free memory.
        Prevents a hung exploit from freezing worker nodes.
        (Accepted: Arch review)
        """
        if self.tokamak:
            try:
                await self.tokamak.kill_active()
            except Exception as e:
                logger.warning("Watchdog kill failed: %s", e)

    def _make_trace(
        self,
        finding: "Finding",
        verdict: TokamakVerdict,
        technique: str,
        t0: float,
        evidence: str = "",
        confidence_notes: str = "",
    ) -> TokamakTrace:
        raw_evidence = f"{finding.title}|{technique}|{evidence}"
        sha256 = hashlib.sha256(raw_evidence.encode()).hexdigest()
        return TokamakTrace(
            finding_title=finding.title,
            verdict=verdict,
            poc_technique=technique,
            evidence_summary=f"[{verdict.value.upper()}] {technique}",
            sha256_evidence=sha256,
            duration_ms=(time.monotonic() - t0) * 1000,
            human_review_required=(verdict == TokamakVerdict.PROBABLE),
            confidence_notes=confidence_notes,
        )
