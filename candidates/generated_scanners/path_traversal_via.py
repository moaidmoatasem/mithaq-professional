import httpx
from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class PathTraversalScanner(BaseScanner):
    """
    CWE-22: Path traversal via directory traversal sequences in file parameters

    Technique: Exploit directory traversal sequences to access files outside the web root.

    Remediation: Sanitize and validate all user inputs to prevent directory traversal attacks.
    """

    tags = ["passive"]

    async def scan(self) -> ScanResult:
        findings = []
        client = httpx.AsyncClient()

        try:
            response = await client.get(
                "http://example.com/vuln.php", params={"file": "../../../etc/passwd"}
            )
            if "\nroot:" in response.text:
                findings.append(
                    Finding(
                        severity=Severity.HIGH,
                        description="Potential path traversal vulnerability detected.",
                        cwe_id="CWE-22",
                    )
                )
        except httpx.ConnectError:
            pass
        except httpx.TimeoutException:
            pass

        return ScanResult(findings=findings)
