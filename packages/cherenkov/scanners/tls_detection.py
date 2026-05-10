"""TLS Scanner — checks if HTTPS is enforced"""

from urllib.parse import urlparse

from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class TLSDetectionScanner(BaseScanner):
    name = "tls_detection"
    description = "Checks if the target enforces HTTPS"

    def __init__(self, name: str = "", description: str = ""):
        super().__init__(name or self.name, description or self.description)

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        findings = []

        parsed = urlparse(target)
        if parsed.scheme != "https":
            findings.append(
                Finding(
                    title="Insecure Protocol (HTTP used)",
                    severity=Severity.HIGH,
                    description="The target uses HTTP instead of HTTPS, exposing data in transit.",
                    cwe="CWE-319",
                    remediation="Enforce HTTPS across all traffic. Redirect HTTP to HTTPS at the server level.",
                )
            )

        return ScanResult(target=target, scanner_name=self.name, findings=findings)
