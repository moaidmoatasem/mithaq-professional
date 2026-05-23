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
                    if content_type and "xml" in content_type:
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


class CVE242Scanner(BaseScanner):
    async def scan(self) -> ScanResult:
        """
        CWE-ISSUE-242: Improper Access Control
        Technique: Failing to Validate Input Data Before Using It
        Remediation: Always validate and sanitize user inputs before using them.

        This scanner checks for potential vulnerabilities due to improper access control.
        """
        url = self.target
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                if "Authorization" not in response.headers:
                    finding = Finding(
                        severity=Severity.HIGH,
                        title="CWE-242: Improper Access Control",
                        description="The target does not include an 'Authorization' header.",
                        cwe="CWE-ISSUE-242",
                        remediation="Always validate and sanitize user inputs before using them.",
                    )
                    return ScanResult(target=self.target, scanner_name="CVE242Scanner", findings=[finding])
        except (httpx.ConnectError, httpx.TimeoutException):
            pass

        return ScanResult(target=self.target, scanner_name="CVE242Scanner", findings=[])


