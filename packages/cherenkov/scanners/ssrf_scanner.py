"""
SSRFScanner — detects Server-Side Request Forgery vulnerabilities.

Tests whether the server will fetch an attacker-supplied URL by injecting
internal/loopback addresses into URL-shaped query parameters.  Uses only
safe, non-destructive addresses (loopback, link-local, APIPA).

CWE-918: Server-Side Request Forgery (SSRF)
OWASP A10:2021 — Server-Side Request Forgery
"""

from __future__ import annotations

import logging
import time
from typing import List
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import httpx

from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity

logger = logging.getLogger("cherenkov.scanners.ssrf")

# Safe internal addresses used as SSRF canaries.
# We never inject real cloud metadata endpoints (169.254.169.254) here
# because this scanner must be safe to run against CBE-regulated systems.
# Loopback variants are enough to confirm the server fetches user-supplied URLs.
_SSRF_CANARIES: list[str] = [
    "http://127.0.0.1/",
    "http://127.0.0.1:22/",
    "http://localhost/",
    "http://[::1]/",
    "http://0.0.0.0/",
    "http://127.1/",
]

# URL-shaped query parameter names that are commonly used to pass URLs.
_URL_PARAM_NAMES: frozenset[str] = frozenset(
    {
        "url",
        "uri",
        "src",
        "source",
        "target",
        "dest",
        "destination",
        "redirect",
        "return",
        "returnUrl",
        "return_url",
        "next",
        "goto",
        "link",
        "feed",
        "host",
        "proxy",
        "fetch",
        "resource",
        "image",
        "img",
        "path",
        "page",
        "ref",
        "referer",
        "referrer",
        "site",
        "website",
        "callback",
        "webhook",
    }
)

# Response characteristics that suggest the server made an outbound connection.
_SSRF_INDICATORS: tuple[str, ...] = (
    # Connection refused / port errors on loopback (server *tried* to connect)
    "connection refused",
    "connection reset",
    "econnrefused",
    "failed to connect",
    "could not connect",
    # SSH banner (port 22 probed)
    "openssh",
    "ssh-",
    # HTTP response from loopback (server fetched and echoed the response)
    "<title>",
    "content-type:",
    "server: ",
    # Generic internal exposure
    "localhost",
    "127.0.0.1",
    "internal server",
)


def _find_url_params(url: str) -> list[str]:
    """Return query parameter names that look like they accept URLs."""
    params = parse_qs(urlparse(url).query, keep_blank_values=True)
    return [k for k in params if k.lower() in _URL_PARAM_NAMES] or list(params.keys())


def _inject_canary(url: str, param: str, canary: str) -> str:
    parsed = urlparse(url)
    params = parse_qs(parsed.query, keep_blank_values=True)
    params[param] = [canary]
    return urlunparse(parsed._replace(query=urlencode(params, doseq=True)))


class SSRFScanner(BaseScanner):
    """
    Injects internal loopback canaries into URL-shaped query parameters and
    checks whether the server echoes connection-attempt artefacts in its response.
    """

    def __init__(self, name: str = "", description: str = ""):
        super().__init__(
            name or "ssrf_scanner",
            description or "Detects Server-Side Request Forgery (CWE-918)",
        )

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        start = time.monotonic()
        findings: List[Finding] = []

        try:
            async with httpx.AsyncClient(timeout=timeout, verify=True) as client:
                url_params = _find_url_params(target)

                # If the URL has no interesting parameters, probe a synthetic one.
                if not url_params:
                    parsed = urlparse(target)
                    synthetic_url = urlunparse(
                        parsed._replace(query=urlencode({"url": "http://127.0.0.1/"}))
                    )
                    probe_list = [(synthetic_url, "url")]
                else:
                    probe_list = [
                        (_inject_canary(target, param, canary), param)
                        for param in url_params
                        for canary in _SSRF_CANARIES[:2]  # Limit probes per param
                    ]

                # Get a baseline response to avoid false positives on static pages.
                try:
                    baseline = await client.get(target, follow_redirects=True)
                    baseline_lower = baseline.text.lower()
                except (httpx.RequestError, httpx.TimeoutException):
                    baseline_lower = ""

                for probe_url, param in probe_list:
                    try:
                        response = await client.get(probe_url, follow_redirects=True)
                    except (httpx.RequestError, httpx.TimeoutException):
                        continue

                    body_lower = response.text.lower()

                    # Indicator must appear in probe response but NOT in baseline.
                    new_indicators = [
                        ind
                        for ind in _SSRF_INDICATORS
                        if ind in body_lower and ind not in baseline_lower
                    ]

                    if response.status_code == 200 and new_indicators:
                        canary_used = probe_url.split(f"{param}=")[-1].split("&")[0]
                        findings.append(
                            Finding(
                                title="Server-Side Request Forgery (SSRF)",
                                severity=Severity.HIGH,
                                description=(
                                    f'Parameter "{param}" appears to trigger a server-side '
                                    f"request when set to {canary_used!r}. "
                                    f"Response contained: {new_indicators[0]!r}. "
                                    f"An attacker may use this to reach internal services, "
                                    f"cloud metadata endpoints, or the host filesystem."
                                ),
                                cwe="CWE-918",
                                remediation=(
                                    "Validate and allowlist any URLs the server fetches on behalf "
                                    "of users. Block requests to RFC-1918, loopback, and cloud "
                                    "metadata address ranges at the network layer. "
                                    "Use an egress proxy that enforces this allowlist. "
                                    "Never forward raw user-supplied URLs to internal HTTP clients."
                                ),
                            )
                        )
                        break  # One confirmed SSRF finding per target is sufficient

        except Exception as exc:
            logger.debug("SSRF scan network/parse error for %s: %s", target, exc)

        duration_ms = (time.monotonic() - start) * 1000

        return ScanResult(
            target=target,
            scanner_name=self.name,
            findings=findings,
            duration_ms=duration_ms,
            status="completed",
        )
