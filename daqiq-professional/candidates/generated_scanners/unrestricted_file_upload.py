import httpx

from daqiq.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class UnrestrictedFileUploadCWE434(BaseScanner):
    def __init__(self):
        super().__init__()
        self.cwe_id = "CWE-434"
        self.technique_used = "Unrestricted file upload with dangerous file type acceptance"
        self.remediation = "Only accept safe file types."
        self.tags = ["passive"]  # Set tags based on the technique used

    async def scan(self) -> ScanResult:
        client = httpx.AsyncClient()
        try:
            url = "http://example.com/upload"  # Replace with actual upload endpoint
            files = {"file": open("dangerous_file.jpg", "rb")}  # Use a dangerous file type
            response = await client.post(url, files=files)
            if response.status_code == 200:
                findings = [
                    Finding(
                        description="Unrestricted file upload with dangerous file type acceptance detected",
                        severity=Severity.HIGH,
                    )
                ]
                return ScanResult(findings=findings)
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            self.logger.error(f"HTTP error occurred: {e}")
        finally:
            await client.aclose()
        return ScanResult()
