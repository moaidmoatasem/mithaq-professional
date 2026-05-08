import httpx

from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class CsrfMissingTokenValidationScanner(BaseScanner):
    """
    CVE-352: Cross-site request forgery missing CSRF token validation

    Technique: Passive scanner

    Remediation: Implement CSRF protection by adding a CSRF token to all POST requests
    that modify the application state or access sensitive resources.

    Set tags to ["passive"] unless it sends payloads (then ["active"]).
    """

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        self.target = target
        result = ScanResult(target=self.target, scanner_name=self.name)
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(self.target)
                if response.status_code == 200:
                    # Check for CSRF token presence in the response
                    csrf_token = self._extract_csrf_token(response.text)
                    if not csrf_token:
                        result.findings.append(
                            Finding(
                                title="CSRF Token Missing",
                                severity=Severity.MEDIUM,
                                description="CSRF token missing in the response from the target endpoint.",
                                cwe="CWE-352",
                                remediation="Implement CSRF protection by adding a CSRF token to all POST requests.",
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

    @staticmethod
    def _extract_csrf_token(html_content: str) -> str:
        # Implement logic to extract CSRF token from HTML content
        # For example, if the CSRF token is in a hidden input field:
        import re

        csrf_token_match = re.search(
            r'<input type="hidden" name="_csrf_token" value="(.*?)">', html_content
        )
        return csrf_token_match.group(1) if csrf_token_match else None

