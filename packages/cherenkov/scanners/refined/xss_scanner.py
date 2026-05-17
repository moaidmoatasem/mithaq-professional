"""XSS Scanner — detects reflected and DOM-based XSS vulnerabilities (CWE-79)"""

import re
import time
from typing import List
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import httpx

from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class XSSScanner(BaseScanner):
    """Detects reflected XSS in URL parameters and DOM XSS sink indicators."""

    XSS_PAYLOADS = [
        '<script>alert("XSS")</script>',
        "<img src=x onerror=alert(1)>",
        '"><svg/onload=alert(1)>',
    ]

    DOM_PATTERNS = [
        r"document\.write\(",
        r"innerHTML\s*=",
        r"eval\(",
        r"\.location\s*=",
    ]

    def __init__(self, name: str = "", description: str = ""):
        super().__init__(
            name or "xss",
            description or "Detects reflected and DOM-based XSS vulnerabilities (CWE-79)",
        )

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        start = time.time()
        findings: List[Finding] = []

        try:
            async with httpx.AsyncClient(
                timeout=timeout, verify=False, follow_redirects=True
            ) as client:
                parsed = urlparse(target)
                params = parse_qs(parsed.query)

                # 1. Reflected XSS — inject payloads into each URL parameter
                for param_name in params:
                    for payload in self.XSS_PAYLOADS:
                        new_params = dict(params)
                        new_params[param_name] = [payload]
                        test_url = urlunparse(
                            parsed._replace(query=urlencode(new_params, doseq=True))
                        )
                        try:
                            resp = await client.get(test_url)
                            if payload in resp.text:
                                findings.append(
                                    Finding(
                                        title="Reflected XSS",
                                        severity=Severity.HIGH,
                                        description=(
                                            f"Payload reflected unescaped in parameter "
                                            f"'{param_name}'. Payload: {payload[:60]}"
                                        ),
                                        cwe="CWE-79",
                                        remediation=(
                                            "HTML-encode all user-supplied input before rendering. "
                                            "Implement a strict Content-Security-Policy."
                                        ),
                                    )
                                )
                                break  # one confirmed payload per parameter is sufficient
                        except (httpx.RequestError, httpx.TimeoutException):
                            continue

                # 2. DOM XSS indicators — fetch base page once
                try:
                    base_resp = await client.get(target)
                    for pattern in self.DOM_PATTERNS:
                        if re.search(pattern, base_resp.text, re.IGNORECASE):
                            findings.append(
                                Finding(
                                    title="Potential DOM XSS Sink",
                                    severity=Severity.MEDIUM,
                                    description=(
                                        f"Dangerous JavaScript pattern detected: {pattern}"
                                    ),
                                    cwe="CWE-79",
                                    remediation=(
                                        "Avoid dangerous sinks (innerHTML, eval, document.write). "
                                        "Use textContent or DOMPurify for untrusted data."
                                    ),
                                )
                            )
                except (httpx.RequestError, httpx.TimeoutException):
                    pass

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
