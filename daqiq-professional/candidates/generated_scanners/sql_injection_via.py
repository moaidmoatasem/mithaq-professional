import httpx

from daqiq.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class SQLInjectionScanner(BaseScanner):
    """
    Scanner for identifying potential SQL injection vulnerabilities through unsanitized user input in query parameters.

    CWE ID: CWE-89
    Technique used: Injection of SQL code into a web application's database.
    Remediation: Use parameterized queries or prepared statements to separate SQL logic from data input, thereby preventing SQL injection attacks.

    Tags: ["passive"]
    """

    async def scan(self) -> ScanResult:
        try:
            # Assuming an endpoint that accepts query parameters
            url = "http://example.com/api"
            query_params = {
                "id": "user_input"  # Unsanitized user input as a query parameter
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=query_params)

            if response.status_code == 200:
                findings = []
                # Assuming the response contains potential SQL injection evidence
                for line in response.text.splitlines():
                    if "SQL Injection detected" in line:
                        finding = Finding(
                            description="Potential SQL injection vulnerability through unsanitized user input.",
                            severity=Severity.INFO,
                        )
                        findings.append(finding)
                return ScanResult(findings=findings)

            return ScanResult(findings=[])

        except httpx.ConnectError as e:
            print(f"Connection error: {e}")
            return ScanResult(findings=[])

        except httpx.TimeoutException as e:
            print(f"Timeout exception: {e}")
            return ScanResult(findings=[])
