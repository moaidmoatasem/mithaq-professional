import httpx

from daqiq.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class DirectoryTraversalScanner(BaseScanner):
    def __init__(self, base_url: str):
        super().__init__("Directory Traversal Scanner")
        self.base_url = base_url
        self.tags = ["passive"]

    async def scan(self) -> ScanResult:
        findings = []

        # Example vulnerable endpoint (CWE-22)
        path_traverse_endpoint = "/path/to/file?file="

        try:
            response = await httpx.AsyncClient().get(
                f"{self.base_url}{path_traverse_endpoint}/../../../../etc/passwd", timeout=5
            )

            if response.status_code == 200 and b"root:" in response.content:
                findings.append(
                    Finding(
                        message="Directory traversal vulnerability detected at /path/to/file?file=/../../../../etc/passwd",
                        severity=Severity.MEDIUM,
                        cwe_id="CWE-22",
                        technique_used="Path traversal via directory traversal sequences in file parameters",
                        remediation="Implement input validation to prevent directory traversal.",
                    )
                )

        except httpx.ConnectError:
            findings.append(
                Finding(
                    message="Failed to connect to the target URL.",
                    severity=Severity.LOW,
                    cwe_id="N/A",
                    technique_used="Connection error during scan",
                    remediation="Check network connectivity and firewall settings.",
                )
            )

        except httpx.TimeoutException:
            findings.append(
                Finding(
                    message="Request timed out.",
                    severity=Severity.LOW,
                    cwe_id="N/A",
                    technique_used="Timeout exception during request",
                    remediation="Increase timeout duration or check server response times.",
                )
            )

        return ScanResult(findings=findings)
