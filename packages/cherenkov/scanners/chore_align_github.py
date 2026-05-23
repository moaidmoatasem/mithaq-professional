import httpx

from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class CustomScanner(BaseScanner):
    """CWE-231: Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection')"""

    async def scan(self) -> ScanResult:
        findings = []
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get("https://example.com")
                if response.status_code != 200:
                    findings.append(Finding(Severity.HIGH, "Unexpected status code"))
            except httpx.ConnectError:
                findings.append(Finding(Severity.MEDIUM, "Connection error"))
            except httpx.TimeoutException:
                findings.append(Finding(Severity.LOW, "Request timed out"))
        return ScanResult(findings)
