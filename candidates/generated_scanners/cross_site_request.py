import httpx
from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class CSRFTokenMissingScanner(BaseScanner):
    """
    CWE-352: Cross-site request forgery missing CSRF token validation

    Technique: This scanner checks for the presence of a CSRF token in HTML forms.

    Remediation: Ensure that all HTML forms include a CSRF token and validate it on the server side.
    """

    async def scan(self) -> ScanResult:
        findings = []
        try:
            client = httpx.AsyncClient()
            response = await client.get(self.target_url)
            if response.status_code == 200:
                content_type = response.headers.get("Content-Type", "")
                if "html" in content_type:
                    form_tags = response.text.split("<form")
                    for tag in form_tags[1:]:
                        if "csrf-token" not in tag.lower():
                            findings.append(
                                Finding(
                                    severity=Severity.MEDIUM,
                                    description="CSRF token missing in form",
                                    recommendation="Add a CSRF token to the form",
                                    tags=["passive"],
                                )
                            )
            else:
                findings.append(
                    Finding(
                        severity=Severity.INFO,
                        description=f"Unexpected HTTP status code {response.status_code}",
                        recommendation="Verify the target URL is correct and accessible",
                        tags=["passive"],
                    )
                )
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            findings.append(
                Finding(
                    severity=Severity.CRITICAL,
                    description=f"Failed to connect or timeout: {e}",
                    recommendation="Check network connectivity and try again later",
                    tags=["passive"],
                )
            )
        finally:
            await client.aclose()

        return ScanResult(target=self.target_url, findings=findings)
