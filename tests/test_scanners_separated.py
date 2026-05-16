import pytest
from cherenkov.scanners.http_methods import HTTPMethodsScanner
from cherenkov.scanners.security_headers import SecurityHeadersScanner
from cherenkov.scanners.tls_detection import TLSDetectionScanner


@pytest.mark.asyncio
async def test_security_headers_returns_result():
    scanner = SecurityHeadersScanner()
    result = await scanner.scan("https://example.com")
    assert result.scanner_name == "security_headers"
    assert result.status == "completed"


@pytest.mark.asyncio
async def test_http_methods_returns_result():
    scanner = HTTPMethodsScanner()
    result = await scanner.scan("https://example.com")
    assert result.scanner_name == "http_methods"


@pytest.mark.asyncio
async def test_tls_detection_detects_http():
    scanner = TLSDetectionScanner()
    result = await scanner.scan("http://example.com")
    assert len(result.findings) == 1
    assert result.findings[0].cwe == "CWE-319"


@pytest.mark.asyncio
async def test_tls_detection_passes_https():
    scanner = TLSDetectionScanner()
    result = await scanner.scan("https://example.com")
    assert len(result.findings) == 0
