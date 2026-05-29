"""Severity Classifier Scanner — classifies potential vulnerability severity of target services"""

from __future__ import annotations

import logging
import re
import time
from typing import Dict, List

import httpx

from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity

logger = logging.getLogger("cherenkov.scanners.severity_classifier")

_SERVER_SEVERITY: Dict[str, Severity] = {
    "apache/2.4.49": Severity.CRITICAL,
    "apache/2.4.50": Severity.CRITICAL,
    "apache/2.4.51": Severity.HIGH,
    "apache/2.2.": Severity.HIGH,
    "iis/6.0": Severity.CRITICAL,
    "iis/7.0": Severity.HIGH,
    "iis/7.5": Severity.HIGH,
    "nginx/0.": Severity.CRITICAL,
    "nginx/1.0": Severity.HIGH,
    "nginx/1.1": Severity.HIGH,
    "php/5.": Severity.CRITICAL,
    "php/7.0": Severity.HIGH,
    "php/7.1": Severity.HIGH,
    "php/7.2": Severity.MEDIUM,
    "php/7.3": Severity.MEDIUM,
    "tomcat/5.": Severity.CRITICAL,
    "tomcat/6.": Severity.HIGH,
    "tomcat/7.": Severity.MEDIUM,
    "openssl/1.0.": Severity.HIGH,
    "openssl/1.1.0": Severity.HIGH,
}

_MISSING_SECURITY_HEADERS: list[tuple[str, str, str]] = [
    (
        "strict-transport-security",
        "CWE-523",
        "HTTP Strict-Transport-Security header is missing, enabling potential MITM attacks.",
    ),
    (
        "content-security-policy",
        "CWE-1021",
        "Content-Security-Policy header is missing, increasing XSS risk.",
    ),
    (
        "x-content-type-options",
        "CWE-16",
        "X-Content-Type-Options header is missing, enabling MIME-type sniffing.",
    ),
    ("x-frame-options", "CWE-1021", "X-Frame-Options header is missing, enabling clickjacking."),
    ("x-xss-protection", "CWE-79", "X-XSS-Protection header is missing (legacy but helpful)."),
]

_INFO_EXPOSURE_PATTERNS: list[tuple[str, Severity, str, str]] = [
    (
        r"laravel|lavarel",
        Severity.HIGH,
        "CWE-200",
        "Server exposes Laravel framework version via headers or response.",
    ),
    (
        r"django|wsgi",
        Severity.MEDIUM,
        "CWE-200",
        "Server exposes Django/Python WSGI framework via headers.",
    ),
    (
        r"rails|ruby on rails",
        Severity.MEDIUM,
        "CWE-200",
        "Server exposes Ruby on Rails via headers.",
    ),
    (
        r"asp\.net|\.net",
        Severity.INFO,
        "CWE-200",
        "Server exposes ASP.NET framework version via headers.",
    ),
    (
        r"wordpress|wp-",
        Severity.MEDIUM,
        "CWE-200",
        "Target appears to run WordPress; ensure it is fully patched.",
    ),
    (
        r"phpmyadmin|pma",
        Severity.HIGH,
        "CWE-200",
        "Target exposes phpMyAdmin interface, a common attack surface.",
    ),
    (
        r"debug|dev|staging|test",
        Severity.HIGH,
        "CWE-200",
        "Target subdomain or path suggests a non-production environment exposed publicly.",
    ),
]


class SeverityClassifierScanner(BaseScanner):
    """Classifies potential vulnerability severity of a target based on exposed services, headers, and technology stack."""

    def __init__(self, name: str = "", description: str = ""):
        super().__init__(
            name or "severity_classifier_scanner",
            description
            or "Classifies target severity based on exposed services, response headers, and technology fingerprints",
        )

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        start = time.monotonic()
        findings: List[Finding] = []

        try:
            async with httpx.AsyncClient(timeout=timeout, verify=True) as client:
                try:
                    response = await client.get(target, follow_redirects=True)
                except (httpx.RequestError, httpx.TimeoutException):
                    duration_ms = (time.monotonic() - start) * 1000
                    return ScanResult(
                        target=target,
                        scanner_name=self.name,
                        findings=[],
                        duration_ms=duration_ms,
                        status="completed",
                    )

                server = response.headers.get("server", "")
                server_lower = server.lower()

                for pattern, severity in _SERVER_SEVERITY.items():
                    if pattern in server_lower:
                        findings.append(
                            Finding(
                                title=f"Known Vulnerable Server Version: {server}",
                                severity=severity,
                                description=(
                                    f"The server header reveals '{server}' which is associated "
                                    f"with known vulnerabilities requiring immediate attention."
                                ),
                                cwe="CWE-1104",
                                remediation="Upgrade the server software to the latest stable version. Apply security patches promptly.",
                            )
                        )
                        break

                for header, cwe, desc in _MISSING_SECURITY_HEADERS:
                    if header not in response.headers:
                        findings.append(
                            Finding(
                                title=f"Missing Security Header: {header}",
                                severity=Severity.LOW,
                                description=desc,
                                cwe=cwe,
                                remediation=f"Configure the server to include the '{header}' header in all responses.",
                            )
                        )

                body_lower = response.text.lower()
                headers_text = str(dict(response.headers)).lower()
                combined = f"{body_lower} {headers_text}"

                for pattern, severity, cwe, desc in _INFO_EXPOSURE_PATTERNS:
                    if re.search(pattern, combined, re.IGNORECASE):
                        findings.append(
                            Finding(
                                title="Technology Stack Information Disclosure",
                                severity=severity,
                                description=desc,
                                cwe=cwe,
                                remediation="Remove version information and framework identifiers from response headers and HTML. Use a reverse proxy to strip unnecessary headers.",
                            )
                        )
                        break

                x_powered = response.headers.get("x-powered-by", "")
                if x_powered:
                    findings.append(
                        Finding(
                            title="Technology Stack Disclosed via X-Powered-By",
                            severity=Severity.INFO,
                            description=(
                                f"The server discloses '{x_powered}' via the X-Powered-By "
                                f"header, providing attackers with version information."
                            ),
                            cwe="CWE-200",
                            remediation="Remove the X-Powered-By header from server responses.",
                        )
                    )

        except Exception as exc:
            logger.debug("SeverityClassifierScanner error for %s: %s", target, exc)

        duration_ms = (time.monotonic() - start) * 1000
        return ScanResult(
            target=target,
            scanner_name=self.name,
            findings=findings,
            duration_ms=duration_ms,
            status="completed",
        )
