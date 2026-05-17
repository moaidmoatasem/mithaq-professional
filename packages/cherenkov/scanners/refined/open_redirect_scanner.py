"""Open Redirect Scanner — detects unvalidated redirect parameters (CWE-601)"""

import time
from typing import List
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import httpx

from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class OpenRedirectScanner(BaseScanner):
    """Detects unvalidated open redirect vulnerabilities in URL parameters."""

    REDIRECT_PARAMS = [
        "url",
        "redirect",
        "next",
        "return",
        "returnTo",
        "goto",
        "target",
        "destination",
        "redir",
        "redirect_uri",
    ]

    # Canary domains — if the response Location header contains these, redirect is open
    REDIRECT_CANARIES = ["http://evil.com", "//evil.com"]
    CANARY_MARKERS = ("evil.com", "attacker.com")

    def __init__(self, name: str = "", description: str = ""):
        super().__init__(
            name or "open_redirect",
            description or "Detects unvalidated open redirect vulnerabilities (CWE-601)",
        )

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        start = time.time()
        findings: List[Finding] = []

        try:
            parsed = urlparse(target)
            params = parse_qs(parsed.query)
            found_redirect_params = [p for p in self.REDIRECT_PARAMS if p in params]

            if found_redirect_params:
                async with httpx.AsyncClient(
                    timeout=timeout, verify=False, follow_redirects=False
                ) as client:
                    for param in found_redirect_params:
                        for canary in self.REDIRECT_CANARIES:
                            new_params = dict(params)
                            new_params[param] = [canary]
                            test_url = urlunparse(
                                parsed._replace(query=urlencode(new_params, doseq=True))
                            )
                            try:
                                resp = await client.get(test_url)
                                if resp.status_code in (301, 302, 303, 307, 308):
                                    location = resp.headers.get("location", "")
                                    if any(m in location for m in self.CANARY_MARKERS):
                                        findings.append(
                                            Finding(
                                                title="Open Redirect",
                                                severity=Severity.MEDIUM,
                                                description=(
                                                    f"Parameter '{param}' redirects to "
                                                    f"attacker-controlled URL: {location}"
                                                ),
                                                cwe="CWE-601",
                                                remediation=(
                                                    "Validate redirect destinations against an "
                                                    "allowlist of trusted URLs. Reject absolute "
                                                    "URLs from user input."
                                                ),
                                            )
                                        )
                                        break  # one confirmed canary per param is sufficient
                            except (httpx.RequestError, httpx.TimeoutException):
                                continue

        except Exception:
            pass

        duration_ms = (time.time() - start) * 1000
        return ScanResult(
            target=target,
            scanner_name=self.name,
            findings=findings,
            duration_ms=duration_ms,
            status="completed",
        )
