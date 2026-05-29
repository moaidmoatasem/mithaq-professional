from unittest.mock import AsyncMock, patch

import pytest
from cherenkov.core.base_scanner import Severity
from cherenkov.scanners.severity_classifier_scanner import SeverityClassifierScanner


@pytest.mark.asyncio
async def test_severity_classifier_detects_vulnerable_server():
    scanner = SeverityClassifierScanner()
    target = "http://example.com"

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = "<html><body>OK</body></html>"
    mock_response.headers = {"server": "Apache/2.4.49", "content-type": "text/html"}

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await scanner.scan(target)

    assert result.target == target
    assert result.status == "completed"
    assert len(result.findings) >= 1
    assert any("Known Vulnerable" in f.title for f in result.findings)
    assert any(f.severity == Severity.CRITICAL for f in result.findings)


@pytest.mark.asyncio
async def test_severity_classifier_detects_missing_security_headers():
    scanner = SeverityClassifierScanner()
    target = "http://example.com"

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = "<html><body>OK</body></html>"
    mock_response.headers = {"content-type": "text/html"}

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await scanner.scan(target)

    assert result.status == "completed"
    missing_header_findings = [f for f in result.findings if "Missing Security Header" in f.title]
    assert len(missing_header_findings) >= 1
    assert all(f.severity == Severity.LOW for f in missing_header_findings)


@pytest.mark.asyncio
async def test_severity_classifier_detects_info_disclosure():
    scanner = SeverityClassifierScanner()
    target = "http://example.com"

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = "<html><body>Powered by Django</body></html>"
    mock_response.headers = {"content-type": "text/html"}

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await scanner.scan(target)

    assert result.status == "completed"
    info_findings = [f for f in result.findings if "Information Disclosure" in f.title]
    assert len(info_findings) >= 1


@pytest.mark.asyncio
async def test_severity_classifier_clean_target():
    scanner = SeverityClassifierScanner()
    target = "http://example.com"

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = "OK"
    mock_response.headers = {
        "strict-transport-security": "max-age=31536000",
        "content-security-policy": "default-src 'self'",
        "x-content-type-options": "nosniff",
        "x-frame-options": "DENY",
        "x-xss-protection": "1; mode=block",
        "content-type": "text/html",
    }

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await scanner.scan(target)

    assert result.status == "completed"
    header_findings = [f for f in result.findings if "Missing Security Header" in f.title]
    assert len(header_findings) == 0


@pytest.mark.asyncio
async def test_severity_classifier_request_timeout():
    scanner = SeverityClassifierScanner()
    target = "http://example.com"

    class FailingClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, *args, **kwargs):
            import httpx

            raise httpx.TimeoutException("Timeout")

    with patch("httpx.AsyncClient", return_value=FailingClient()):
        result = await scanner.scan(target)

    assert result.status == "completed"
    assert len(result.findings) == 0


@pytest.mark.asyncio
async def test_severity_classifier_x_powered_by():
    scanner = SeverityClassifierScanner()
    target = "http://example.com"

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = "<html><body>OK</body></html>"
    mock_response.headers = {
        "x-powered-by": "PHP/7.4.33",
        "content-type": "text/html",
    }

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await scanner.scan(target)

    assert result.status == "completed"
    powered_findings = [f for f in result.findings if "X-Powered-By" in f.title]
    assert len(powered_findings) >= 1
