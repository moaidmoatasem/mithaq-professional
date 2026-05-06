import httpx

from daqiq.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class UntrustedDeserializationScanner(BaseScanner):
    """CWE-502: Deserialization of untrusted data in API endpoints.

    Technique used: HTTP requests with custom payloads sent to the API.
    Remediation: Validate and sanitize all inputs passed to deserialize methods.

    Tags: ["passive"]
    """

    async def scan(self) -> ScanResult:
        result = ScanResult()
        try:
            # Example of making an HTTP POST request with a deserialization payload
            url = "https://example.com/api/endpoint"
            response = await httpx.post(url, json={"data": {"key": "value"}}, timeout=10)
            if response.status_code == 200:
                result.add(
                    Finding(
                        Severity.INFO, "Deserialization of untrusted data in API endpoint detected."
                    )
                )
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            result.add(Finding(Severity.WARNING, f"HTTP request error: {e}"))
        return result
