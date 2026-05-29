"""Static File Upload Scanner — analyzes response content and URLs for file upload-related vulnerabilities"""

from __future__ import annotations

import logging
import re
import time
from typing import List
from urllib.parse import parse_qs, urlparse

import httpx

from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity

logger = logging.getLogger("cherenkov.scanners.static_file_upload")

_DANGEROUS_EXTENSIONS: list[str] = [
    ".php",
    ".phtml",
    ".php3",
    ".php4",
    ".php5",
    ".pht",
    ".jsp",
    ".jspx",
    ".war",
    ".asp",
    ".aspx",
    ".asa",
    ".cer",
    ".cfm",
    ".cfc",
    ".pl",
    ".cgi",
    ".py",
    ".rb",
    ".exe",
    ".sh",
    ".bash",
    ".cmd",
    ".bat",
    ".ps1",
    ".htaccess",
    ".shtml",
]

_UPLOAD_ENDPOINT_PATTERNS: list[str] = [
    "upload",
    "file-upload",
    "fileupload",
    "import",
    "media",
    "attach",
    "attachment",
    "profile-pic",
    "avatar",
    "image-upload",
    "doc-upload",
    "resume",
]

_UPLOAD_SUCCESS_INDICATORS: list[str] = [
    "uploaded successfully",
    "upload successful",
    "file uploaded",
    "upload complete",
    "attachment saved",
    "file saved",
    "image uploaded",
]


class StaticFileUploadScanner(BaseScanner):
    """Detects unrestricted file upload vulnerabilities by analyzing endpoint patterns and response content."""

    def __init__(self, name: str = "", description: str = ""):
        super().__init__(
            name or "static_file_upload_scanner",
            description
            or "Static analysis scanner for unrestricted file upload vulnerabilities (CWE-434)",
        )

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        start = time.monotonic()
        findings: List[Finding] = []

        parsed = urlparse(target)
        path = parsed.path.lower()

        for ext in _DANGEROUS_EXTENSIONS:
            if path.endswith(ext):
                findings.append(
                    Finding(
                        title="Dangerous File Extension in URL",
                        severity=Severity.HIGH,
                        description=(
                            f"The target URL references a file with a dangerous extension "
                            f"('{ext}'). If user-uploaded content is served with its original "
                            f"extension, this may enable remote code execution."
                        ),
                        cwe="CWE-434",
                        remediation=(
                            "Validate file extensions and MIME types server-side. "
                            "Store uploaded files outside the web root with randomized names. "
                            "Disable script execution in upload directories."
                        ),
                    )
                )
                break

        query_extensions = parse_qs(parsed.query).get("ext", []) + parse_qs(parsed.query).get(
            "extension", []
        )
        for ext_param in query_extensions:
            if f".{ext_param.lower()}" in _DANGEROUS_EXTENSIONS or ext_param.lower() in [
                e.lstrip(".") for e in _DANGEROUS_EXTENSIONS
            ]:
                findings.append(
                    Finding(
                        title="File Extension Specified in Query Parameter",
                        severity=Severity.MEDIUM,
                        description=(
                            f"The URL query parameter specifies a file extension "
                            f"('{ext_param}') that may allow arbitrary file type uploads."
                        ),
                        cwe="CWE-434",
                        remediation=(
                            "Do not allow clients to specify file extensions. "
                            "Derive file types from server-side MIME detection, "
                            "not from user-supplied parameters."
                        ),
                    )
                )
                break

        is_upload_endpoint = any(p in path for p in _UPLOAD_ENDPOINT_PATTERNS)

        try:
            async with httpx.AsyncClient(timeout=timeout, verify=True) as client:
                try:
                    response = await client.get(target, follow_redirects=True)
                except (httpx.RequestError, httpx.TimeoutException):
                    duration_ms = (time.monotonic() - start) * 1000
                    return ScanResult(
                        target=target,
                        scanner_name=self.name,
                        findings=findings,
                        duration_ms=duration_ms,
                        status="completed",
                    )

                if is_upload_endpoint:
                    body_lower = response.text.lower()
                    matched_indicator = next(
                        (ind for ind in _UPLOAD_SUCCESS_INDICATORS if ind in body_lower), None
                    )

                    if matched_indicator:
                        findings.append(
                            Finding(
                                title="File Upload Endpoint Detected",
                                severity=Severity.INFO,
                                description=(
                                    f"The target at '{path}' appears to be a file upload endpoint. "
                                    f"Response contains '{matched_indicator}', suggesting file "
                                    f"uploads are accepted. Verify that upload validation is properly "
                                    f"configured."
                                ),
                                cwe="CWE-434",
                                remediation=(
                                    "Review file upload validation logic. Ensure extension, "
                                    "MIME type, and content inspection are performed server-side. "
                                    "Implement size limits and store files securely."
                                ),
                            )
                        )

                    form_inputs = re.findall(
                        r'<input[^>]*type=["\']file["\'][^>]*>', response.text, re.IGNORECASE
                    )
                    if form_inputs:
                        findings.append(
                            Finding(
                                title="File Input Field Found on Upload Endpoint",
                                severity=Severity.INFO,
                                description=(
                                    f"The upload endpoint contains {len(form_inputs)} file input "
                                    f"field(s). Review the server-side validation to ensure "
                                    f"unrestricted uploads are not possible."
                                ),
                                cwe="CWE-434",
                                remediation=(
                                    "Ensure server-side validation checks file type, "
                                    "size, and content. Use an allowlist of permitted "
                                    "extensions and MIME types."
                                ),
                            )
                        )

        except Exception as exc:
            logger.debug("StaticFileUploadScanner error for %s: %s", target, exc)

        duration_ms = (time.monotonic() - start) * 1000
        return ScanResult(
            target=target,
            scanner_name=self.name,
            findings=findings,
            duration_ms=duration_ms,
            status="completed",
        )
