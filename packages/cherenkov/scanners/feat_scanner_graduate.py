import httpx
from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class AttackChainDetector(BaseScanner):
    """CWE-244: Insecure Deserialization
    Technique: Exploiting insecure deserialization vulnerabilities in web applications.
    Remediation: Avoid using libraries known to be vulnerable. Ensure proper serialization and validation of data.
    """

    async def scan(self) -> ScanResult:
        findings = []
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.target)
                if "pickle" in response.text.lower():
                    findings.append(
                        Finding(
                            severity=Severity.HIGH,
                            description="Insecure deserialization vulnerability detected",
                            evidence=response.text,
                        )
                    )
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            findings.append(
                Finding(
                    severity=Severity.INFO, description=f"Connection error: {e}", evidence=str(e)
                )
            )

        return ScanResult(target=self.target, findings=findings, tags=["passive"])
