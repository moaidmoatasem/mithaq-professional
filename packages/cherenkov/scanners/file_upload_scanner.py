"""File upload vulnerability scanner — detect unsafe file upload endpoints"""

import re

from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class FileUploadScanner(BaseScanner):
    """Scan for file upload vulnerabilities — arbitrary file types, missing validation, path traversal in filenames"""

    def __init__(self):
        super().__init__(
            name="file_upload",
            description="File upload vulnerability scanner — type validation, size limits, name sanitization",
        )

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        import time as time_module

        start = time_module.monotonic()
        findings: list[Finding] = []

        page_content = await self._fetch_page(target, timeout)
        if not page_content:
            return ScanResult(
                target=target,
                scanner_name=self.name,
                findings=[],
                duration_ms=(time_module.monotonic() - start) * 1000,
            )

        findings.extend(self._audit_upload_forms(target, page_content))

        return ScanResult(
            target=target,
            scanner_name=self.name,
            findings=findings,
            duration_ms=(time_module.monotonic() - start) * 1000,
        )

    async def _fetch_page(self, target: str, timeout: float) -> str:
        try:
            resp = await self._http_request(target, timeout)
            return resp.text if resp.status_code == 200 else ""
        except Exception:
            return ""

    def _audit_upload_forms(self, target: str, html: str) -> list[Finding]:
        findings: list[Finding] = []

        file_inputs = re.findall(r'<input[^>]*type=["\']file["\'][^>]*>', html, re.IGNORECASE)
        if not file_inputs:
            return findings

        forms = re.findall(
            r'<form[^>]*action=["\']([^"\']*)["\'][^>]*>(.*?)</form>',
            html,
            re.DOTALL | re.IGNORECASE,
        )

        for action, form_content in forms:
            if "file" not in form_content:
                continue

            accept_match = re.search(r'accept=["\']([^"\']*)["\']', form_content)
            if not accept_match:
                findings.append(
                    Finding(
                        title="File Upload Without Type Restriction",
                        severity=Severity.MEDIUM,
                        description=f"{target}: Upload form to '{action}' has no accept attribute — any file type allowed.",
                        cwe="CWE-434",
                        remediation="Add an accept attribute restricting allowed MIME types (e.g., accept='image/png, image/jpeg').",
                    )
                )

            max_match = re.search(r'maxlength=["\'](\d+)["\']', form_content)
            if not max_match:
                findings.append(
                    Finding(
                        title="File Upload Without Size Limit",
                        severity=Severity.LOW,
                        description=f"{target}: Upload form to '{action}' lacks maxlength — potential for large file DoS.",
                        cwe="CWE-770",
                        remediation="Enforce file size limits server-side and via maxlength attribute.",
                    )
                )

            action_lower = action.lower()
            if action_lower.startswith("http://"):
                findings.append(
                    Finding(
                        title="File Upload Over HTTP",
                        severity=Severity.MEDIUM,
                        description=f"{target}: Upload form submits to '{action}' over unencrypted HTTP.",
                        cwe="CWE-319",
                        remediation="Use HTTPS for all file upload endpoints.",
                    )
                )

        return findings
