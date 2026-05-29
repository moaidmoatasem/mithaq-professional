from unittest.mock import AsyncMock, patch

import pytest
from cherenkov.core.base_scanner import Severity
from cherenkov.scanners.static_file_upload_scanner import StaticFileUploadScanner


@pytest.mark.asyncio
async def test_static_file_upload_dangerous_extension():
    scanner = StaticFileUploadScanner()
    target = "http://example.com/uploads/shell.php"

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = "OK"

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await scanner.scan(target)

    assert result.target == target
    assert result.status == "completed"
    assert len(result.findings) >= 1
    assert any("Dangerous File Extension" in f.title for f in result.findings)
    assert any(f.severity == Severity.HIGH for f in result.findings)


@pytest.mark.asyncio
async def test_static_file_upload_clean_extension():
    scanner = StaticFileUploadScanner()
    target = "http://example.com/images/photo.jpg"

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = "OK"

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await scanner.scan(target)

    assert result.status == "completed"
    assert len(result.findings) == 0


@pytest.mark.asyncio
async def test_static_file_upload_upload_endpoint():
    scanner = StaticFileUploadScanner()
    target = "http://example.com/upload"

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = "File uploaded successfully"
    mock_response.headers = {"content-type": "text/html"}

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await scanner.scan(target)

    assert result.status == "completed"
    assert len(result.findings) >= 1
    upload_finding = next((f for f in result.findings if "Upload Endpoint" in f.title), None)
    assert upload_finding is not None
    assert upload_finding.severity == Severity.INFO


@pytest.mark.asyncio
async def test_static_file_upload_param_extension():
    scanner = StaticFileUploadScanner()
    target = "http://example.com/upload?ext=jsp"

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = "OK"

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await scanner.scan(target)

    assert result.status == "completed"
    assert len(result.findings) >= 1
    assert any("Query Parameter" in f.title for f in result.findings)


@pytest.mark.asyncio
async def test_static_file_upload_request_timeout():
    scanner = StaticFileUploadScanner()
    target = "http://example.com/"

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
