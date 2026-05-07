import httpx

from mithaq.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class TLSValidationScanner(BaseScanner):
    """
    CWE-295: Improper TLS certificate validation and expired cert detection.

    Technique: HTTP request to a server with known insecure configuration.
    Remediation: Implement proper TLS certificate validation in your application code
                 by checking the chain of trust and validity dates of certificates.
    Tags: passive
    """

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        self.target = target
        result = ScanResult(target=self.target, scanner_name=self.name)
        try:
            async with httpx.AsyncClient(timeout=timeout, verify=True) as client:
                response = await client.get(self.target)

                if response.status_code == 200:
                    # In a real scanner, we would check the certificate details here
                    pass
        except httpx.ConnectError as e:
            if "SSL" in str(e) or "CERTIFICATE" in str(e).upper():
                result.findings.append(
                    Finding(
                        title="Improper TLS Certificate",
                        severity=Severity.HIGH,
                        description=f"TLS certificate validation failed: {str(e)}",
                        cwe="CWE-295",
                        remediation="Ensure the server has a valid, trusted TLS certificate.",
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

