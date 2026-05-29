from unittest.mock import AsyncMock, patch

import pytest
from cherenkov.core.base_scanner import Severity
from cherenkov.scanners.local_path_traversal_scanner import LocalPathTraversalScanner


@pytest.mark.asyncio
async def test_local_path_traversal_detects_traversal_pattern():
    scanner = LocalPathTraversalScanner()
    target = "http://example.com/../../../etc/passwd"

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = "OK"

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await scanner.scan(target)

    assert result.target == target
    assert result.status == "completed"
    assert len(result.findings) >= 1
    assert any("traversal pattern" in f.title.lower() for f in result.findings)
    assert any(f.severity == Severity.HIGH for f in result.findings)


@pytest.mark.asyncio
async def test_local_path_traversal_clean_target():
    scanner = LocalPathTraversalScanner()
    target = "http://example.com/index.html"

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = "Welcome"

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await scanner.scan(target)

    assert result.status == "completed"
    assert len(result.findings) == 0


@pytest.mark.asyncio
async def test_local_path_traversal_sensitive_path():
    scanner = LocalPathTraversalScanner()
    target = "http://example.com/files?path=/etc/passwd"

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = "OK"

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await scanner.scan(target)

    assert result.status == "completed"
    assert len(result.findings) >= 1
    assert any("Sensitive" in f.title for f in result.findings)


@pytest.mark.asyncio
async def test_local_path_traversal_url_encoded():
    scanner = LocalPathTraversalScanner()
    target = "http://example.com/%2e%2e%2f%2e%2e%2fetc/passwd"

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = "OK"

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await scanner.scan(target)

    assert result.status == "completed"
    assert len(result.findings) >= 1


@pytest.mark.asyncio
async def test_local_path_traversal_request_timeout():
    scanner = LocalPathTraversalScanner()
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
