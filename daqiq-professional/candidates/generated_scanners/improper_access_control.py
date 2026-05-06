import httpx

from daqiq.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class ImproperAccessControlScanner(BaseScanner):
    """
    CWE-284: Improper access control on authenticated endpoints

    Technique used: Passive scanning by checking the response status codes and headers.

    Remediation in one sentence: Implement proper authentication mechanisms and authorization checks for all API endpoints to prevent unauthorized access.

    Scanner tags: ["passive"]
    """

    async def scan(self) -> ScanResult:
        # Assuming 'self.target' is a string representing the target URL
        try:
            async with httpx.AsyncClient() as client:
                # Sending a GET request to the target URL
                response = await client.get(self.target)

                # Handling common status codes
                if response.status_code in [401, 403]:
                    findings = [
                        Finding(
                            message=f"Access denied: {response.status_code}",
                            severity=Severity.LOW,
                            tags=["authentication", "access-denied"],
                        )
                    ]
                else:
                    findings = []

            return ScanResult(findings=findings)

        except httpx.ConnectError as e:
            # Handle connection errors
            return ScanResult(failures=[Finding(message=str(e), severity=Severity.HIGH)])

        except httpx.TimeoutException as e:
            # Handle timeout exceptions
            return ScanResult(failures=[Finding(message=str(e), severity=Severity.MEDIUM)])
