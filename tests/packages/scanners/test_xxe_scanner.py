from unittest.mock import MagicMock, patch

import pytest
import httpx
from cherenkov.core.base_scanner import Severity
from cherenkov.scanners.xxe_scanner import XXEScanner


@pytest.mark.asyncio
async def test_xxe_scanner_vulnerable_linux():
    scanner = XXEScanner()

    mock_response = MagicMock(spec=httpx.Response)
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
        result = await scanner.scan("http://vulnerable.com/xml")

        assert len(result.findings) == 1
        finding = result.findings[0]
        assert finding.severity == Severity.HIGH
        assert finding.cwe == "CWE-611"
        assert "matched 'root:x:0:0:'" in finding.description


@pytest.mark.asyncio
async def test_xxe_scanner_vulnerable_windows():
    scanner = XXEScanner()

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.text = "[extensions]\nbitmapped=off"

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, *args, **kwargs):
            return mock_response

    with patch("httpx.AsyncClient", return_value=MockClient()):
        result = await scanner.scan("http://vulnerable-win.com/xml")

        assert len(result.findings) == 1
        finding = result.findings[0]
        assert "matched '[extensions]'" in finding.description


@pytest.mark.asyncio
async def test_xxe_scanner_safe():
    scanner = XXEScanner()

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.text = "<?xml version='1.0'?><root>OK</root>"

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, *args, **kwargs):
            return mock_response

    with patch("httpx.AsyncClient", return_value=MockClient()):
        result = await scanner.scan("http://safe.com/xml")

        assert len(result.findings) == 0


@pytest.mark.asyncio
async def test_xxe_scanner_timeout():
    scanner = XXEScanner()

    with patch("httpx.AsyncClient.post", side_effect=httpx.TimeoutException("Timeout")):
        # Note: We patch AsyncClient.post directly if we don't want to mock the whole context manager
        # But wait, the scanner uses 'async with httpx.AsyncClient(...) as client'
        # So we need to mock the client returned by the context manager

        class MockClient:
            async def __aenter__(self): return self
            async def __aexit__(self, *args): pass
            async def post(self, *args, **kwargs):
                raise httpx.TimeoutException("Timeout")

        with patch("httpx.AsyncClient", return_value=MockClient()):
            result = await scanner.scan("http://timeout.com/xml")
            assert len(result.findings) == 0
            assert result.status == "completed"
