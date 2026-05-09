"""HTTP Methods Scanner — checks for dangerous HTTP methods"""

import httpx
from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class HTTPMethodsScanner(BaseScanner):
    name = "http_methods"
    description = "Checks for dangerous HTTP methods (PUT, DELETE, TRACE, CONNECT)"

    def __init__(self, name: str = "", description: str = ""):
        super().__init__(name or self.name, description or self.description)

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        findings = []
        dangerous = ["PUT", "DELETE", "TRACE", "CONNECT"]

        async with httpx.AsyncClient(timeout=timeout, verify=True) as client:
            for method in dangerous:
                try:
                    response = await client.request(method, target)
                    if response.status_code not in (405, 501):
                        findings.append(Finding(
                            title=f"Dangerous HTTP Method Enabled: {method}",
                            severity=Severity.HIGH,
                            description=f"The {method} method is allowed (Status: {response.status_code})",
                            cwe="CWE-749",
                            remediation=f"Disable the {method} method in server configuration.",
                        ))
                except (httpx.ConnectError, httpx.TimeoutException, httpx.RemoteProtocolError):
                    pass

        return ScanResult(target=target, scanner_name=self.name, findings=findings)
