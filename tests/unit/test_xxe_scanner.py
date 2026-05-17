from unittest.mock import MagicMock, patch

import httpx
import pytest
from cherenkov.core.base_scanner import Severity
from cherenkov.scanners.xxe_scanner import XXEScanner


@pytest.mark.asyncio
async def test_xxe_scanner_positive():
    scanner = XXEScanner()
    target = "http://example.com/api"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "root:x:0:0:root:/root:/bin/bash"

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, *args, **kwargs):
            return mock_response

    with patch("httpx.AsyncClient", return_value=MockClient()):
        result = await scanner.scan(target)

    assert result.target == target
    assert len(result.findings) == 1
    assert result.findings[0].severity == Severity.HIGH
    assert "XXE" in result.findings[0].title


@pytest.mark.asyncio
async def test_xxe_scanner_negative():
    scanner = XXEScanner()
    target = "http://example.com/api"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "OK"

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, *args, **kwargs):
            return mock_response

    with patch("httpx.AsyncClient", return_value=MockClient()):
        result = await scanner.scan(target)

    assert len(result.findings) == 0


@pytest.mark.asyncio
async def test_xxe_scanner_timeout():
    scanner = XXEScanner()
    target = "http://example.com/api"

    with patch("httpx.AsyncClient", side_effect=httpx.TimeoutException("Timeout")):
        result = await scanner.scan(target)

    assert len(result.findings) == 0
    assert result.status == "completed"
