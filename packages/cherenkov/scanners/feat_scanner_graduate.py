import httpx
from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class XXEScanner(BaseScanner):
    """CWE-241: External Entity (XXE) Injection - Detect potential XXE vulnerabilities by checking for external entity processing in XML documents.

    Technique: Passive scanner that checks XML responses for evidence of XXE.

    Remediation: Ensure that XML parsers are configured to disable external entity processing.
    """

    async def scan(self) -> ScanResult:
        findings = []
        tags = ["passive"]

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.target)
                if response.status_code == 200:
                    content_type = response.headers.get("Content-Type")
                    if "xml" in content_type:
                        xml_content = response.text
                        if "<!DOCTYPE" in xml_content or "&entity;" in xml_content:
                            findings.append(
                                Finding(
                                    title="Potential XXE Injection",
                                    description="The XML response contains external entity processing potential.",
                                    severity=Severity.MEDIUM,
                                    tags=["xxe", "xml"],
                                )
                            )

        except (httpx.ConnectError, httpx.TimeoutException):
            pass

        return ScanResult(target=self.target, findings=findings, tags=tags)
