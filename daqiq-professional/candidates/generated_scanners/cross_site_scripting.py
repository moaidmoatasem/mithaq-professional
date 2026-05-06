import httpx

from daqiq.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class XssScanner(BaseScanner):
    """
    CWE-79: Cross-site scripting via reflected query parameters.

    Technique used: Analyze input received in the URL to detect potential script injection.
    Remediation: Validate and sanitize all user inputs to prevent XSS attacks.

    Scanner tags: ["passive"]
    """

    async def scan(self) -> ScanResult:
        try:
            # Example target URL
            url = "https://example.com/search?query=malicious<script>alert('XSS')</script>"

            # Send a GET request with the crafted query parameter
            response = await httpx.AsyncClient().get(url)

            if "alert" in response.text:
                return ScanResult(
                    findings=[
                        Finding(
                            title="Potential XSS vulnerability",
                            description="Detected potential cross-site scripting via reflected query parameters.",
                            severity=Severity.LOW,
                        )
                    ]
                )
        except httpx.ConnectError:
            return ScanResult(failures=["Connection error"])
        except httpx.TimeoutException:
            return ScanResult(failures=["Timeout"])

        return ScanResult()
