import httpx
from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class CORSMisconfigurationScanner(BaseScanner):
    """
    CWE-942: CORS misconfiguration allowing wildcard or reflected origins

    Technique: Test for CORS misconfiguration by sending requests with wildcard origins.
    Remediation: Ensure that the CORS policy does not allow wildcard or reflected origins.
    """

    tags = ["passive"]

    async def scan(self) -> ScanResult:
        url = self.target.url
        findings = []

        try:
            async with httpx.AsyncClient() as client:
                headers = {"Origin": "*"}
                response = await client.options(url, headers=headers)

                if (
                    "Access-Control-Allow-Origin" in response.headers
                    and response.headers["Access-Control-Allow-Origin"] == "*"
                ):
                    findings.append(
                        Finding(
                            severity=Severity.HIGH,
                            title="CORS Misconfiguration with Wildcard Origin",
                            description=f"The target {url} allows wildcard CORS origin ('*'). This can lead to security vulnerabilities.",
                            cwe_id="CWE-942",
                        )
                    )

                if "Access-Control-Allow-Origin" in response.headers and response.headers[
                    "Access-Control-Allow-Origin"
                ].endswith(".example.com"):
                    findings.append(
                        Finding(
                            severity=Severity.MEDIUM,
                            title="CORS Misconfiguration with Reflected Origin",
                            description=f"The target {url} allows CORS origin that reflects the request host ('{response.headers['Access-Control-Allow-Origin']}'). This can be exploited to perform Cross-Site Scripting (XSS) attacks.",
                            cwe_id="CWE-942",
                        )
                    )

        except httpx.ConnectError:
            findings.append(
                Finding(
                    severity=Severity.INFO,
                    title="Connection Error",
                    description=f"Could not connect to {url}. Check the target URL and network connectivity.",
                    cwe_id=None,
                )
            )

        except httpx.TimeoutException:
            findings.append(
                Finding(
                    severity=Severity.INFO,
                    title="Timeout Error",
                    description=f"Request to {url} timed out. Increase timeout settings if necessary.",
                    cwe_id=None,
                )
            )

        return ScanResult(finding_count=len(findings), findings=findings)
