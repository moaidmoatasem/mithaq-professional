import httpx

from daqiq.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class CorsMisconfigScanner(BaseScanner):
    """
    Scans for CORS misconfiguration allowing wildcard or reflected origins.

    CWE ID: CWE-942
    Technique used: Checks the 'Access-Control-Allow-Origin' header in HTTP responses.
    Remediation in one sentence: Configure CORS to allow only specific origins, not wildcards or reflections.

    Tags: passive
    """

    async def scan(self) -> ScanResult:
        findings = []
        try:
            with httpx.AsyncClient() as client:
                response = await client.get("https://example.com")
                if "Access-Control-Allow-Origin" in response.headers and (
                    response.headers["Access-Control-Allow-Origin"] == "*"
                    or response.headers["Access-Control-Allow-Origin"].find("/") != -1
                ):
                    findings.append(
                        Finding(
                            title="CORS Misconfiguration",
                            description="The server allows wildcard or reflected origins.",
                            severity=Severity.WARNING,
                            remediation="Configure CORS to allow only specific origins.",
                        )
                    )
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            findings.append(
                Finding(
                    title="Scan Error",
                    description=f"Failed to connect to the target: {str(e)}",
                    severity=Severity.ERROR,
                )
            )

        return ScanResult(findings=findings)
