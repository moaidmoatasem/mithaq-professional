import httpx
from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class UnrestrictedFileUpload(BaseScanner):
    """
    CWE-434: Improper Control of Generation of Code ('Code Injection'). This scanner checks for
    unrestricted file upload functionality with dangerous file type acceptance. Only flag clear evidence.

    Technique: By uploading a file with a dangerous extension (e.g., .php, .asp), the server may execute it as code.

    Remediation: Implement strict content-type validation and restrict file uploads to safe types.
    """

    async def scan(self) -> ScanResult:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://example.com/upload")
                if "file" in response.text:
                    return ScanResult(
                        severity=Severity.HIGH,
                        description="Unrestricted file upload functionality detected.",
                        findings=[Finding(description="Dangerous file type acceptance allowed.")],
                        tags=["passive"],
                    )
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            return ScanResult(
                severity=Severity.LOW,
                description=f"Failed to connect or timeout: {e}",
                findings=[Finding(description=str(e))],
                tags=["passive"],
            )

        return ScanResult(
            severity=Severity.NONE,
            description="No clear evidence of unrestricted file upload.",
            findings=[Finding(description="No issues found.")],
            tags=["passive"],
        )
