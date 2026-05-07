import httpx

from mithaq.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class ImproperAccessControlScanner(BaseScanner):
    """
    CWE-284: Improper access control on authenticated endpoints

    Technique used: Passive scanning by checking the response status codes and headers.

    Remediation in one sentence: Implement proper authentication mechanisms and authorization checks for all API endpoints to prevent unauthorized access.

    Scanner tags: ["passive"]
    """

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        self.target = target
        result = ScanResult(target=self.target, scanner_name=self.name)
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                # Sending a GET request to the target URL
                response = await client.get(self.target)

                # Handling common status codes
                if response.status_code in [401, 403]:
                    result.findings.append(
                        Finding(
                            title="Access Control Mechanism Present",
                            description=f"The endpoint returned {response.status_code}, indicating access control is active.",
                            severity=Severity.INFO,
                            cwe="CWE-284",
                            remediation="Ensure proper authorization checks are also implemented.",
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

