"""Local Path Traversal Scanner — analyzes URL/URI paths for traversal patterns"""

from __future__ import annotations

import logging
import time
from typing import List
from urllib.parse import unquote, urlparse

import httpx

from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity

logger = logging.getLogger("cherenkov.scanners.local_path_traversal")

_TRAVERSAL_PATTERNS: list[str] = [
    "../",
    "..\\",
    "%2e%2e%2f",
    "%2e%2e\\",
    "..%252f",
    "%c0%ae%c0%ae%c0%af",
    "....//",
    "..;/",
]

_SENSITIVE_FILE_PATTERNS: list[str] = [
    "/etc/passwd",
    "/etc/shadow",
    "/etc/ssl/",
    "/windows/win.ini",
    "/windows/system32/",
    "/.env",
    "/.git/config",
    "/WEB-INF/web.xml",
]


class LocalPathTraversalScanner(BaseScanner):
    """Detects path traversal patterns and sensitive file exposure in URL paths."""

    def __init__(self, name: str = "", description: str = ""):
        super().__init__(
            name or "local_path_traversal_scanner",
            description
            or "Analyzes URL/URI paths for traversal patterns and sensitive file exposure (CWE-22)",
        )

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        start = time.monotonic()
        findings: List[Finding] = []

        try:
            parsed = urlparse(target)
            path = unquote(parsed.path)
            query = unquote(parsed.query)

            combined = f"{path}?{query}" if query else path

            for pattern in _TRAVERSAL_PATTERNS:
                if pattern in combined.lower():
                    findings.append(
                        Finding(
                            title="Path Traversal Pattern Detected in URI",
                            severity=Severity.HIGH,
                            description=(
                                f"The target URI contains a path traversal pattern "
                                f"('{pattern}') which may indicate directory traversal "
                                f"vulnerability or an attempt to access restricted files."
                            ),
                            cwe="CWE-22",
                            remediation=(
                                "Validate and sanitize all user-supplied input used in file paths. "
                                "Use a safe allowlist of permitted paths and avoid passing user "
                                "input directly to filesystem APIs."
                            ),
                        )
                    )
                    break

            for sensitive in _SENSITIVE_FILE_PATTERNS:
                if sensitive in combined.lower():
                    findings.append(
                        Finding(
                            title="Sensitive File Path Reference in URI",
                            severity=Severity.MEDIUM,
                            description=(
                                f"The target URI references a sensitive file path "
                                f"('{sensitive}'). This may expose confidential system "
                                f"files or configuration."
                            ),
                            cwe="CWE-200",
                            remediation=(
                                "Ensure sensitive system files and configuration paths are "
                                "not exposed through URL routing. Restrict access to "
                                "server-side resources through proper access controls."
                            ),
                        )
                    )
                    break

            async with httpx.AsyncClient(timeout=timeout, verify=True) as client:
                try:
                    response = await client.get(target, follow_redirects=True)
                    response_body = response.text.lower()
                    for sensitive in _SENSITIVE_FILE_PATTERNS:
                        keyword = sensitive.split("/")[-1]
                        if keyword in response_body and keyword not in ("", "."):
                            findings.append(
                                Finding(
                                    title="Sensitive Content Leaked in Response",
                                    severity=Severity.HIGH,
                                    description=(
                                        f"The response body contains '{keyword}' which may "
                                        f"indicate that a sensitive file was exposed through "
                                        f"path traversal."
                                    ),
                                    cwe="CWE-22",
                                    remediation=(
                                        "Implement strict access controls on file-serving "
                                        "endpoints. Use chroot jails or virtual path mapping "
                                        "to prevent directory traversal."
                                    ),
                                )
                            )
                            break
                except (httpx.RequestError, httpx.TimeoutException):
                    pass

        except Exception as exc:
            logger.debug("LocalPathTraversalScanner error for %s: %s", target, exc)

        duration_ms = (time.monotonic() - start) * 1000
        return ScanResult(
            target=target,
            scanner_name=self.name,
            findings=findings,
            duration_ms=duration_ms,
            status="completed",
        )
