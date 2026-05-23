import httpx
from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class ExampleScanner(BaseScanner):
    """CWE-235: Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection')"""

    async def scan(self) -> ScanResult:
        results = []
        client = httpx.AsyncClient()
        try:
            response = await client.get("https://example.com")
            response.raise_for_status()
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            result = Finding(
                severity=Severity.HIGH,
                description=f"Connection error or timeout: {e}",
            )
            results.append(result)
        else:
            if "<script>" in response.text:
                result = Finding(
                    severity=Severity.MEDIUM,
                    description="Potential OS Command Injection vulnerability detected",
                )
                results.append(result)

        return ScanResult(failures=results)
