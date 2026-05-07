import httpx

from mithaq.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class UnrestrictedFileUploadCWE434(BaseScanner):
    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        self.target = target
        result = ScanResult(target=self.target, scanner_name=self.name)
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                # Mock a file upload attempt
                files = {"file": ("test.php", b"<?php echo 'vulnerable'; ?>", "application/x-php")}
                response = await client.post(self.target, files=files)
                if response.status_code == 200:
                    result.findings.append(
                        Finding(
                            title="Unrestricted File Upload",
                            description="Unrestricted file upload with dangerous file type acceptance detected.",
                            severity=Severity.HIGH,
                            cwe="CWE-434",
                            remediation="Only accept safe file types and validate file content.",
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

