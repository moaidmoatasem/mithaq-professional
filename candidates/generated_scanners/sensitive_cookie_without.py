import httpx
from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class CookieSecurityScanner(BaseScanner):
    """
    CWE-614: Sensitive cookie without Secure and HttpOnly flags

    Technique: Check for the presence of 'Secure' and 'HttpOnly' flags on cookies.

    Remediation: Ensure all cookies set by your application have both 'Secure' and 'HttpOnly' flags.
    """

    async def scan(self) -> ScanResult:
        findings = []
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.target_url)
                cookies = response.cookies
                for cookie_name, cookie in cookies.items():
                    if not (cookie.secure and cookie.httponly):
                        findings.append(
                            Finding(
                                title=f"Sensitive Cookie '{cookie_name}' without Secure and HttpOnly flags",
                                description="The cookie is accessible via client-side scripts. It should be marked with 'Secure' and 'HttpOnly'.",
                                severity=Severity.HIGH,
                                cwe_id="CWE-614",
                            )
                        )
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            findings.append(
                Finding(
                    title="Connection error",
                    description=f"Failed to connect to {self.target_url}: {str(e)}",
                    severity=Severity.INFO,
                    cwe_id=None,
                )
            )

        return ScanResult(
            scanner_name=self.__class__.__name__,
            target_url=self.target_url,
            findings=findings,
            tags=["passive"],
        )
