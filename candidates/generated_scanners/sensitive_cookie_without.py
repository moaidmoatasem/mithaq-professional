import httpx

from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class SensitiveCookieScanner(BaseScanner):
    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        self.target = target
        result = ScanResult(target=self.target, scanner_name=self.name)
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(self.target, follow_redirects=True)

                if "Set-Cookie" in response.headers:
                    cookies = response.headers.get_list("Set-Cookie")
                    for cookie in cookies:
                        parts = [p.strip().lower() for p in cookie.split(";")]
                        key = cookie.split(";")[0].split("=")[0].strip()

                        # Check for Secure and HttpOnly flags
                        secure_flag = "secure" in parts
                        httponly_flag = "httponly" in parts

                        if not secure_flag or not httponly_flag:
                            result.findings.append(
                                Finding(
                                    title="Insecure Cookie Flags",
                                    description=f"Cookie '{key}' is missing Secure or HttpOnly flags.",
                                    severity=Severity.MEDIUM,
                                    cwe="CWE-614",
                                    remediation="Ensure that all sensitive cookies are marked as 'Secure' and 'HttpOnly'.",
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

