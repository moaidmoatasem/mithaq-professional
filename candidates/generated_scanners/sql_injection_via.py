import httpx
from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class SQLInjectionScanner(BaseScanner):
    """
    CWE-89: Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection')

    Technique: Attackers exploit the lack of proper input validation to inject malicious SQL code into a query.

    Remediation: Always sanitize user inputs and use parameterized queries or prepared statements.
    """

    async def scan(self) -> ScanResult:
        results = []
        client = httpx.AsyncClient()
        try:
            response = await client.get("http://example.com/vuln", params={"search": "' OR '1'='1"})
            if "admin" in response.text:
                results.append(
                    Finding(
                        title="SQL Injection Vulnerability",
                        description="The application is vulnerable to SQL injection via unsanitized user input in query parameters.",
                        severity=Severity.HIGH,
                        tags=["passive"],
                    )
                )
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            results.append(
                Finding(
                    title="HTTP Request Error",
                    description=f"An error occurred during the HTTP request: {e}",
                    severity=Severity.LOW,
                    tags=["passive"],
                )
            )
        finally:
            await client.aclose()
        return ScanResult(findings=results)
