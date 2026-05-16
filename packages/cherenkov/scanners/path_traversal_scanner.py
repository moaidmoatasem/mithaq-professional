"""Path Traversal Scanner"""

import time
from typing import List

import httpx

from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class PathTraversalScanner(BaseScanner):
    """Scanner to detect Path Traversal vulnerabilities."""

    def __init__(self, name: str = "", description: str = ""):
        super().__init__(name, description)

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        """Execute the scan - attempting directory traversal payloads against the target."""
        start_time = time.time()
        findings: List[Finding] = []

        # Test payloads for path traversal
        payloads = [
            "../../../etc/passwd",
            "..%2f..%2f..%2fetc%2fpasswd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
        ]

        try:
            async with httpx.AsyncClient(timeout=timeout, verify=True) as client:
                for payload in payloads:
                    # Append the payload to the target URL. Assuming the target is a vulnerable endpoint like /download?file=
                    # We will append the payload to the URL and check the response.
                    test_url = target
                    if not test_url.endswith("/"):
                        test_url += "/"
                    test_url += payload

                    response = await client.get(test_url, follow_redirects=True)

                    if response.status_code == 200 and "root:x:0:0:" in response.text:
                        findings.append(
                            Finding(
                                title="Path Traversal",
                                severity=Severity.HIGH,
                                description=f"The application is vulnerable to Path Traversal. Using payload '{payload}', local file contents (/etc/passwd) were exposed.",
                                cwe="CWE-22",
                                remediation="Ensure user input is strictly validated. Use secure APIs for accessing files, avoid using direct file paths, or use functions like os.path.abspath and ensure it starts with the intended base directory.",
                            )
                        )
                        # Stop after the first finding to avoid duplicate reports
                        break
        except (httpx.RequestError, httpx.TimeoutException):
            pass

        duration_ms = (time.time() - start_time) * 1000

        return ScanResult(
            target=target,
            scanner_name=self.name,
            findings=findings,
            duration_ms=duration_ms,
            status="completed",
        )
