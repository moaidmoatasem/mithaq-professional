import httpx
from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class ExampleScanner(BaseScanner):
    """
    CWE-240: Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection')
    """

    async def scan(self) -> ScanResult:
        findings = []
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("https://example.com")
                if response.status_code != 200:
                    finding = Finding(
                        severity=Severity.HIGH,
                        description="Non-200 status code received from example.com",
                    )
                    findings.append(finding)
        except httpx.ConnectError as e:
            finding = Finding(
                severity=Severity.CRITICAL,
                description=f"Connection error: {e}",
            )
            findings.append(finding)
        except httpx.TimeoutException as e:
            finding = Finding(
                severity=Severity.CRITICAL,
                description=f"Timeout error: {e}",
            )
            findings.append(finding)

        return ScanResult(findings=findings)
