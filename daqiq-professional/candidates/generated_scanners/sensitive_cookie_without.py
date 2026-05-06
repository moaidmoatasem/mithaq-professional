import httpx

from daqiq.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class SensitiveCookieScanner(BaseScanner):
    async def scan(self) -> ScanResult:
        """
        This function scans for sensitive cookies without the Secure and HttpOnly flags.

        CWE ID: CWE-614 - Insecure Cookie Usage
        Technique Used: Passive scanning by checking headers on HTTP responses.
        Remediation in one sentence: Ensure that all cookies are marked as "Secure" and "HttpOnly".

        Returns:
            ScanResult containing findings of sensitive cookies without Secure and HttpOnly flags.
        """
        result = ScanResult()
        async with httpx.AsyncClient() as client:
            try:
                # Simulate a GET request to gather information about cookies
                response = await client.get("https://example.com", follow_redirects=True)

                if "Set-Cookie" in response.headers:
                    cookies = response.headers["Set-Cookie"].split(", ")
                    for cookie in cookies:
                        parts = cookie.split(";")
                        key = parts[0].strip()

                        # Check for Secure and HttpOnly flags
                        secure_flag = any(part.startswith("Secure") for part in parts)
                        httponly_flag = any(part.startswith("HttpOnly") for part in parts)

                        if not secure_flag or not httponly_flag:
                            finding = Finding(
                                url=response.url,
                                message=f"Sensitive cookie found: {key}. No Secure and HttpOnly flags.",
                                severity=Severity.MEDIUM,
                            )
                            result.findings.append(finding)
            except (httpx.ConnectError, httpx.TimeoutException) as e:
                result.add_error(str(e))

        # Set tags based on whether we sent payloads or not
        if not client.session.headers:
            result.tags = ["passive"]
        else:
            result.tags = ["active"]

        return result
