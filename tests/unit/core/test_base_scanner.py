import pytest
from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


def test_base_scanner_cannot_instantiate_directly():
    with pytest.raises(TypeError):
        BaseScanner()


def test_base_scanner_implementation():
    class TestScanner(BaseScanner):
        async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
            return ScanResult(target=target, scanner_name=self.name)

    scanner = TestScanner()
    assert scanner.name == "TestScanner"
    assert scanner.description == "TestScanner scanner"
    assert scanner.version == "1.0.0"


@pytest.mark.asyncio
async def test_scan_result():
    class TestScanner(BaseScanner):
        async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
            finding = Finding(
                title="Test Finding",
                severity=Severity.HIGH,
                description="A test finding",
                cwe="CWE-79",
                remediation="Fix it",
            )
            return ScanResult(
                target=target, scanner_name=self.name, findings=[finding], duration_ms=100.0
            )

    scanner = TestScanner()
    result = await scanner.scan("http://example.com")
    assert result.target == "http://example.com"
    assert result.scanner_name == "TestScanner"
    assert len(result.findings) == 1
    assert result.findings[0].title == "Test Finding"
    assert result.findings[0].severity == Severity.HIGH
    assert result.duration_ms == 100.0
    assert result.status == "completed"


from unittest.mock import MagicMock, patch


@pytest.mark.asyncio
async def test_http_request():
    class TestScanner(BaseScanner):
        async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
            return ScanResult(target=target, scanner_name=self.name)

    scanner = TestScanner()

    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        response = await scanner._http_request("http://example.com", timeout=10.0)

        assert response.status_code == 200
        mock_get.assert_called_once_with("http://example.com", follow_redirects=True)
