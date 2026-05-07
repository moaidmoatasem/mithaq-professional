import httpx

from mithaq.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class SQLInjectionScanner(BaseScanner):
    """
    Scanner for identifying potential SQL injection vulnerabilities through unsanitized user input in query parameters.

    CWE ID: CWE-89
    Technique used: Injection of SQL code into a web application's database.
    Remediation: Use parameterized queries or prepared statements to separate SQL logic from data input, thereby preventing SQL injection attacks.

    Tags: ["passive"]
    """

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        self.target = target
        result = ScanResult(target=self.target, scanner_name=self.name)
        try:
            # Assuming an endpoint that accepts query parameters
            query_params = {
                "id": "' OR '1'='1"  # Potential SQLi payload
            }

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(self.target, params=query_params)

            if response.status_code == 200:
                # Assuming the response contains potential SQL injection evidence
                if any(indicator in response.text for indicator in ["SQL syntax", "mysql_fetch_array", "SQL Injection detected"]):
                    result.findings.append(
                        Finding(
                            title="Potential SQL Injection",
                            description="Potential SQL injection vulnerability through unsanitized user input in query parameters.",
                            severity=Severity.HIGH,
                            cwe="CWE-89",
                            remediation="Use parameterized queries or prepared statements.",
                        )
                    )

        except (httpx.ConnectError, httpx.TimeoutException) as e:
            result.status = "failed"
            result.findings.append(
                Finding(
                    title="Scan Error",
                    description=f"Failed to connect to the target: {str(e)}",
                    severity=Severity.HIGH,
                    remediation="Check network connectivity and target availability.",
                    cwe="N/A",
                )
            )

        return result

