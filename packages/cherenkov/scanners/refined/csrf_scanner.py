"""CSRF Scanner — detects missing CSRF token protection (CWE-352)"""

import re
import time
from typing import List

import httpx

from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class CSRFScanner(BaseScanner):
    """Detects missing CSRF token protection and insecure SameSite cookie attributes."""

    CSRF_TOKEN_PATTERNS = [
        r"csrf[_-]?token",
        r"\b_token\b",
        r"authenticity[_-]?token",
        r"__RequestVerificationToken",
    ]

    def __init__(self, name: str = "", description: str = ""):
        super().__init__(
            name or "csrf",
            description or "Detects missing CSRF token protection (CWE-352)",
        )

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        start = time.time()
        findings: List[Finding] = []

        try:
            response = await self._http_request(target, timeout)
            content = response.text
            headers = response.headers

            # 1. Check for forms without CSRF tokens
            forms = re.findall(r"<form[^>]*>", content, re.IGNORECASE)
            if forms:
                has_csrf = any(
                    re.search(p, content, re.IGNORECASE)
                    for p in self.CSRF_TOKEN_PATTERNS
                )
                if not has_csrf:
                    findings.append(
                        Finding(
                            title="Missing CSRF Token",
                            severity=Severity.HIGH,
                            description=(
                                f"Found {len(forms)} form(s) with no detectable CSRF token. "
                                "State-changing requests may be vulnerable to CSRF attacks."
                            ),
                            cwe="CWE-352",
                            remediation=(
                                "Include a per-session, unpredictable CSRF token in every "
                                "state-changing form and validate it server-side."
                            ),
                        )
                    )

            # 2. Check SameSite cookie attribute
            set_cookie = headers.get("set-cookie", "")
            if set_cookie and "samesite" not in set_cookie.lower():
                findings.append(
                    Finding(
                        title="Missing SameSite Cookie Attribute",
                        severity=Severity.MEDIUM,
                        description=(
                            "Session cookies are missing the SameSite attribute, "
                            "weakening CSRF defenses."
                        ),
                        cwe="CWE-352",
                        remediation=(
                            "Set SameSite=Lax or SameSite=Strict on all session cookies."
                        ),
                    )
                )

        except (httpx.RequestError, httpx.TimeoutException):
            pass

        duration_ms = (time.time() - start) * 1000
        return ScanResult(
            target=target,
            scanner_name=self.name,
            findings=findings,
            duration_ms=duration_ms,
            status="completed",
        )
