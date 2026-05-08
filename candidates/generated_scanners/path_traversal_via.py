import httpx

from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class DirectoryTraversalScanner(BaseScanner):
    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        self.target = target
        result = ScanResult(target=self.target, scanner_name=self.name)

        # Example vulnerable endpoint (CWE-22)
        test_url = f"{self.target}/../../../../etc/passwd"

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(test_url)

                if response.status_code == 200 and b"root:" in response.content:
                    result.findings.append(
                        Finding(
                            title="Directory Traversal Vulnerability",
                            description="Detected potential path traversal via directory traversal sequences.",
                            severity=Severity.HIGH,
                            cwe="CWE-22",
                            remediation="Implement input validation to prevent directory traversal.",
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

