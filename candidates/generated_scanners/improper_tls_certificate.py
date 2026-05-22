import httpx
from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class TlsCertificateScanner(BaseScanner):
    """CWE-295: Improper TLS certificate validation and expired cert detection.
    Technique: Check for invalid or expired TLS certificates during HTTPS connections.
    Remediation: Ensure proper TLS certificate validation and renewal."""

    tags = ["passive"]

    async def scan(self) -> ScanResult:
        findings = []
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.target, timeout=5)
                if response.status_code == 200:
                    cert_info = response.connection.properties["ssl"]
                    if not cert_info.is_valid():
                        findings.append(
                            Finding(
                                severity=Severity.HIGH,
                                description="Invalid or expired TLS certificate detected.",
                                cwe_id="CWE-295",
                            )
                        )
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            findings.append(
                Finding(severity=Severity.INFO, description=f"Connection error: {e}", cwe_id="N/A")
            )
        return ScanResult(target=self.target, findings=findings)
