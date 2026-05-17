"""
XSSScanner — detects reflected Cross-Site Scripting vulnerabilities.

Injects inert XSS probe strings into URL query parameters and checks
whether the server echoes the payload back unescaped in the HTML body.
No JavaScript is executed; this is purely a reflection test.

CWE-79: Improper Neutralization of Input During Web Page Generation
OWASP A03:2021 — Injection
"""

from __future__ import annotations

import logging
import time
from typing import List
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import httpx

from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity

logger = logging.getLogger("cherenkov.scanners.xss")

# Probe strings — HTML/JS canaries that are safe to send but unmistakable
# when reflected without encoding.  We look for the *raw* canary in the body
# to avoid false positives from URL-encoded reflections.
_XSS_PROBES: list[tuple[str, str]] = [
    # (payload, unique_marker_we_search_for_in_response)
    ("<script>cherenkov_xss</script>", "<script>cherenkov_xss</script>"),
    ('<img src=x onerror="cherenkov_xss">', 'onerror="cherenkov_xss"'),
    ("'><svg/onload=cherenkov_xss>", "<svg/onload=cherenkov_xss>"),
    ('"--><script>cherenkov_xss</script>', "<script>cherenkov_xss</script>"),
    ("javascript:cherenkov_xss", "javascript:cherenkov_xss"),
]


def _inject_into_params(url: str, payload: str) -> list[str]:
    """Return URLs with each query parameter replaced by *payload* in turn."""
    parsed = urlparse(url)
    params = parse_qs(parsed.query, keep_blank_values=True)
    if not params:
        # No params — inject via a synthetic search= parameter.
        return [urlunparse(parsed._replace(query=urlencode({"search": payload})))]

    result: list[str] = []
    for key in params:
        modified = dict(params)
        modified[key] = [payload]
        result.append(urlunparse(parsed._replace(query=urlencode(modified, doseq=True))))
    return result


class XSSScanner(BaseScanner):
    """
    Reflected XSS scanner — injects HTML/JS canaries into query parameters
    and checks whether the server echoes them back without HTML-encoding.
    """

    def __init__(self, name: str = "", description: str = ""):
        super().__init__(
            name or "xss_scanner",
            description or "Detects reflected Cross-Site Scripting (CWE-79)",
        )

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        start = time.monotonic()
        findings: List[Finding] = []

        try:
            async with httpx.AsyncClient(timeout=timeout, verify=True) as client:
                for payload, marker in _XSS_PROBES:
                    probe_urls = _inject_into_params(target, payload)
                    for probe_url in probe_urls:
                        try:
                            response = await client.get(probe_url, follow_redirects=True)
                        except (httpx.RequestError, httpx.TimeoutException):
                            continue

                        if response.status_code == 200 and marker.lower() in response.text.lower():
                            findings.append(
                                Finding(
                                    title="Reflected Cross-Site Scripting (XSS)",
                                    severity=Severity.HIGH,
                                    description=(
                                        f"The server reflected an unescaped XSS payload in its "
                                        f'response. Probe: "{payload[:60]}". '
                                        f"Marker found in response body indicates the input is "
                                        f"rendered as raw HTML, enabling script injection in "
                                        f"victim browsers."
                                    ),
                                    cwe="CWE-79",
                                    remediation=(
                                        "HTML-encode all user-supplied input before rendering it "
                                        "in the DOM. Apply a Content-Security-Policy header that "
                                        "restricts script sources. Use a framework template engine "
                                        "with auto-escaping enabled (e.g., Jinja2 autoescape, "
                                        "React JSX). Never use innerHTML with untrusted data."
                                    ),
                                )
                            )
                            break  # One confirmed finding per target is sufficient
                    if findings:
                        break

        except Exception as exc:
            logger.debug("XSS scan network/parse error for %s: %s", target, exc)

        duration_ms = (time.monotonic() - start) * 1000

        return ScanResult(
            target=target,
            scanner_name=self.name,
            findings=findings,
            duration_ms=duration_ms,
            status="completed",
        )
