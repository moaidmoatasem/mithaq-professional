"""File Upload Scanner -- detects unsafe server-side file upload handling (CWE-434)"""

import time
from typing import List

import httpx

from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity

_UPLOAD_SUCCESS_MARKERS = (
    "uploaded successfully",
    "upload complete",
    "file saved",
)

_PROBE_FILES = [
    ("shell.php", "application/x-php"),
    ("shell.php5", "application/x-php"),
    ("shell.phtml", "application/x-php"),
]


def _probe_payload() -> bytes:
    return b"CHERENKOV_PROBE_UPLOAD_TEST"


class FileUploadScanner(BaseScanner):
    UPLOAD_PATHS = ["/upload", "/api/upload", "/file/upload", "/files"]

    def __init__(self, name: str = "", description: str = ""):
        super().__init__(
            name or "file_upload",
            description or "Detects unsafe server-side file upload handling (CWE-434)",
        )

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        start = time.time()
        findings: List[Finding] = []
        base = target.rstrip("/")
        try:
            async with httpx.AsyncClient(timeout=timeout, verify=False, follow_redirects=True) as client:
                payload = _probe_payload()
                for path in self.UPLOAD_PATHS:
                    url = base + path
                    for filename, mime_type in _PROBE_FILES:
                        try:
                            resp = await client.post(url, files={"file": (filename, payload, mime_type)})
                            body = resp.text.lower()
                            if resp.status_code == 200 and any(m in body for m in _UPLOAD_SUCCESS_MARKERS):
                                findings.append(Finding(
                                    title="Unsafe File Upload",
                                    severity=Severity.HIGH,
                                    description=f"Server accepted a dangerous file upload at {url}. Filename: {filename}",
                                    cwe="CWE-434",
                                    remediation="Validate file extensions and MIME types server-side.",
                                ))
                                break
                        except (httpx.RequestError, httpx.TimeoutException):
                            continue
                    if findings:
                        break
        except (httpx.RequestError, httpx.TimeoutException):
            pass
        duration_ms = (time.time() - start) * 1000
        return ScanResult(target=target, scanner_name=self.name, findings=findings, duration_ms=duration_ms, status="completed")
