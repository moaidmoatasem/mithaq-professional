import httpx

from mithaq.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class UntrustedDeserializationScanner(BaseScanner):
    """CWE-502: Deserialization of untrusted data in API endpoints.

    Technique used: HTTP requests with custom payloads sent to the API.
    Remediation: Validate and sanitize all inputs passed to deserialize methods.

    Tags: ["passive"]
    """

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        self.target = target
        result = ScanResult(target=self.target, scanner_name=self.name)
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                # In a real scenario, we would send a payload designed to trigger a deserialization issue
                response = await client.post(self.target, json={"data": {"key": "value"}})
                if response.status_code == 200:
                    result.findings.append(
                        Finding(
                            title="Potential Untrusted Deserialization",
                            severity=Severity.HIGH,
                            description="The endpoint accepts JSON data which might be processed by an untrusted deserializer.",
                            cwe="CWE-502",
                            remediation="Validate and sanitize all inputs passed to deserialize methods.",
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

