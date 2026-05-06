import httpx

from daqiq.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class CsrfMissingTokenValidationScanner(BaseScanner):
    """
    CVE-352: Cross-site request forgery missing CSRF token validation

    Technique: Passive scanner

    Remediation: Implement CSRF protection by adding a CSRF token to all POST requests
    that modify the application state or access sensitive resources.

    Set tags to ["passive"] unless it sends payloads (then ["active"]).
    """

    def __init__(self, url: str):
        self.url = url

    async def scan(self) -> ScanResult:
        result = ScanResult(tags=["passive"])
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.url}/some-endpoint")
                if response.status_code == 200:
                    # Check for CSRF token presence in the response
                    csrf_token = self._extract_csrf_token(response.text)
                    if not csrf_token:
                        findings = [
                            Finding(
                                cwe="CWE-352",
                                severity=Severity.MEDIUM,
                                message="CSRF token missing",
                            )
                        ]
                        result.findings.extend(findings)

        except httpx.ConnectError as e:
            result.add_error(Finding(error_message=str(e), severity=Severity.HIGH))
        except httpx.TimeoutException as e:
            result.add_error(Finding(error_message=str(e), severity=Severity.MEDIUM))

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
