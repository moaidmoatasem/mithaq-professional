import httpx

from mithaq.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class XssScanner(BaseScanner):
    """
    CWE-79: Cross-site scripting via reflected query parameters.

    Technique used: Analyze input received in the URL to detect potential script injection.
    Remediation: Validate and sanitize all user inputs to prevent XSS attacks.

    Scanner tags: ["passive"]
    """

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        self.target = target
        result = ScanResult(target=self.target, scanner_name=self.name)
        try:
            # Send a GET request with a potential XSS payload
            # In a real scanner, we would test multiple parameters
            test_url = f"{self.target}/search?query=malicious<script>alert('XSS')</script>"
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(test_url)

                if "alert" in response.text:
                    result.findings.append(
                        Finding(
                            title="Potential XSS vulnerability",
                            description="Detected potential cross-site scripting via reflected query parameters.",
                            severity=Severity.HIGH,
                            cwe="CWE-79",
                            remediation="Validate and sanitize all user inputs to prevent XSS attacks.",
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

