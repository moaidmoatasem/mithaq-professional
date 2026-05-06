import httpx

from daqiq.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class TLSValidationScanner(BaseScanner):
    """
    CWE-295: Improper TLS certificate validation and expired cert detection.

    Technique: HTTP request to a server with known insecure configuration.
    Remediation: Implement proper TLS certificate validation in your application code
                 by checking the chain of trust and validity dates of certificates.
    Tags: passive
    """

    async def scan(self) -> ScanResult:
        try:
            url = "https://example.com"  # Replace with the target URL
            async with httpx.AsyncClient() as client:
                response = await client.get(url)

                if response.status_code == 200:
                    finding = Finding(
                        severity=Severity.WARNING,
                        message="Insecure TLS configuration detected.",
                        additional_info=f"Server responded with status code {response.status_code}.",
                    )
                    return ScanResult(finding_list=[finding])
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            finding = Finding(
                severity=Severity.INFO,
                message=f"An error occurred while scanning {url}: {e}",
                additional_info="Please check the network connection or server status.",
            )
            return ScanResult(finding_list=[finding])
