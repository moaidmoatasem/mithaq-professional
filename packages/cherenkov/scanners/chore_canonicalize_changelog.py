import httpx

from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class MyScanner(BaseScanner):
    async def scan(self) -> ScanResult:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://example.com")
                if response.status_code == 200:
                    return ScanResult(
                        severity=Severity.INFO,
                        findings=[Finding(description="Success", cwe_id="CWE-235")],
                    )
                else:
                    return ScanResult(
                        severity=Severity.WARN,
                        findings=[
                            Finding(
                                description=f"Unexpected status code: {response.status_code}",
                                cwe_id="CWE-235",
                            )
                        ],
                    )
        except httpx.ConnectError as e:
            return ScanResult(
                severity=Severity.CRITICAL, findings=[Finding(description=str(e), cwe_id="CWE-235")]
            )
        except httpx.TimeoutException as e:
            return ScanResult(
                severity=Severity.ERROR, findings=[Finding(description=str(e), cwe_id="CWE-235")]
            )

    __doc__ = """
    This is a sample scanner for demonstrating security checks.
    CWE-ISSUE-235
    """
