import httpx

from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class CorsMisconfigScanner(BaseScanner):
    """
    Scans for CORS misconfiguration allowing wildcard or reflected origins.

    CWE ID: CWE-942
    Technique used: Checks the 'Access-Control-Allow-Origin' header in HTTP responses.
    Remediation in one sentence: Configure CORS to allow only specific origins, not wildcards or reflections.

    Tags: passive
    """

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        self.target = target
        result = ScanResult(target=self.target, scanner_name=self.name)
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(self.target)
                if "Access-Control-Allow-Origin" in response.headers and (
                    response.headers["Access-Control-Allow-Origin"] == "*"
                    or response.headers["Access-Control-Allow-Origin"].find("/") != -1
                ):
                    result.findings.append(
                        Finding(
                            title="CORS Misconfiguration",
                            description="The server allows wildcard or reflected origins.",
                            severity=Severity.MEDIUM,
                            remediation="Configure CORS to allow only specific origins.",
                            cwe="CWE-942",
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

