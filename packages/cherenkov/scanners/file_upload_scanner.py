"""
FileUploadScanner — detects unrestricted file upload vulnerabilities.

Tests whether a target endpoint accepts uploads of dangerous file types
that could enable server-side code execution. Content is intentionally
inert; only the file extension matters for testing the server allowlist.

CWE-434: Unrestricted Upload of File with Dangerous Type
OWASP A05:2021 — Security Misconfiguration
"""

from __future__ import annotations

import logging
import time
from typing import List

import httpx

from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity

logger = logging.getLogger("cherenkov.scanners.file_upload")

# Probe filenames paired with MIME types. Content is a benign marker string.
# We test whether the server rejects the *extension*, not the content.
_UPLOAD_PROBES: list[tuple[str, str]] = [
    ("shell.php", "application/octet-stream"),
    ("shell.jsp", "application/octet-stream"),
    ("shell.aspx", "application/octet-stream"),
    ("shell.phtml", "application/octet-stream"),
]

_PROBE_CONTENT = b"cherenkov-upload-probe"

# Response body substrings that indicate the server accepted the upload.
_SUCCESS_INDICATORS = (
    "uploaded successfully",
    "upload successful",
    "file uploaded",
    "successfully uploaded",
    "upload complete",
)


class FileUploadScanner(BaseScanner):
    """
    Probes a URL for unrestricted file upload by POSTing files with
    server-side script extensions and checking whether they are accepted.
    """

    def __init__(self, name: str = "", description: str = ""):
        super().__init__(
            name or "file_upload_scanner",
            description or "Detects unrestricted file upload (CWE-434)",
        )

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        start = time.monotonic()
        findings: List[Finding] = []

        try:
            async with httpx.AsyncClient(timeout=timeout, verify=True) as client:
                for filename, content_type in _UPLOAD_PROBES:
                    try:
                        response = await client.post(
                            target,
                            files={"file": (filename, _PROBE_CONTENT, content_type)},
                            follow_redirects=True,
                        )
                    except (httpx.RequestError, httpx.TimeoutException):
                        continue

                    body_lower = response.text.lower()
                    filename_in_body = filename in response.text
                    success_phrase = any(p in body_lower for p in _SUCCESS_INDICATORS)

                    if response.status_code == 200 and (filename_in_body or success_phrase):
                        findings.append(
                            Finding(
                                title="Unrestricted File Upload",
                                severity=Severity.HIGH,
                                description=(
                                    f"The endpoint accepted a file with a dangerous extension "
                                    f"({filename}). If the upload directory is web-accessible "
                                    f"this may enable remote code execution."
                                ),
                                cwe="CWE-434",
                                remediation=(
                                    "Validate file extensions and MIME types server-side. "
                                    "Store uploads outside the web root or in object storage. "
                                    "Rename files on upload and disable script execution "
                                    "in the upload directory."
                                ),
                            )
                        )
                        break  # One confirmed finding is sufficient per scan

        except Exception as exc:
            logger.debug("File-upload scan network error for %s: %s", target, exc)

        duration_ms = (time.monotonic() - start) * 1000

        return ScanResult(
            target=target,
            scanner_name=self.name,
            findings=findings,
            duration_ms=duration_ms,
            status="completed",
        )
