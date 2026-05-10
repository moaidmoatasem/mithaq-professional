"""Security Headers Scanner — checks for missing HTTP security headers"""

from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class SecurityHeadersScanner(BaseScanner):
    name = "security_headers"
    description = "Checks for missing HTTP security headers"

    def __init__(self, name: str = "", description: str = ""):
        super().__init__(name or self.name, description or self.description)

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        findings = []
        try:
            response = await self._http_request(target, timeout)
            headers = response.headers

            checks = {
                "X-Frame-Options": (
                    Severity.MEDIUM,
                    "Protects against clickjacking",
                    "CWE-1021",
                    "Configure the server to emit the X-Frame-Options header (e.g., DENY or SAMEORIGIN).",
                ),
                "X-Content-Type-Options": (
                    Severity.MEDIUM,
                    "Prevents MIME sniffing",
                    "CWE-693",
                    "Configure the server to emit the X-Content-Type-Options: nosniff header.",
                ),
                "Strict-Transport-Security": (
                    Severity.MEDIUM,
                    "Enforces HTTPS connections",
                    "CWE-523",
                    "Configure the server to emit the Strict-Transport-Security header with a sufficient max-age.",
                ),
                "Content-Security-Policy": (
                    Severity.MEDIUM,
                    "Prevents XSS and data injection attacks",
                    "CWE-693",
                    "Configure the server to emit a Content-Security-Policy header restricting allowed sources.",
                ),
                "X-XSS-Protection": (
                    Severity.LOW,
                    "Legacy XSS protection header",
                    "CWE-693",
                    "Configure the server to emit the X-XSS-Protection header.",
                ),
            }

            for header, (severity, purpose, cwe, remediation) in checks.items():
                if header not in headers:
                    findings.append(
                        Finding(
                            title=f"Missing Security Header: {header}",
                            severity=severity,
                            description=f"Missing {header} ({purpose})",
                            cwe=cwe,
                            remediation=remediation,
                        )
                    )
        except Exception:
            return ScanResult(
                target=target,
                scanner_name=self.name,
                status="failed",
                findings=[],
            )

        return ScanResult(target=target, scanner_name=self.name, findings=findings)
