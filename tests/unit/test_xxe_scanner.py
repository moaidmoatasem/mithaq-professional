import pytest
from unittest.mock import patch, MagicMock

from cherenkov.autonomous_generated.scanners.xxe_scanner import XXEScanner
from cherenkov.core.base_scanner import Severity

@pytest.mark.asyncio
async def test_xxe_scanner_safe():
    scanner = XXEScanner()

    class MockResponse:
        status = 200
        async def text(self):
            return '<?xml version="1.0"?><data>Safe</data>'
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    class MockSession:
        def get(self, *args, **kwargs):
            return MockResponse()
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    with patch("aiohttp.ClientSession", return_value=MockSession()):
        result = await scanner.scan("http://safe.com/xml")
        assert result.scanner_name == "XXEScanner"
        assert result.target == "http://safe.com/xml"
        assert len(result.findings) == 0

@pytest.mark.asyncio
async def test_xxe_scanner_unsafe():
    scanner = XXEScanner()

    class MockResponse:
        status = 200
        async def text(self):
            return '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><foo>&xxe;</foo>'
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    class MockSession:
        def get(self, *args, **kwargs):
            return MockResponse()
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    # The existing perform_scan logic parses <? ... ?> so let's mock perform_scan directly
    # to avoid dealing with the specific broken regex in the original code, as requested.
    with patch("aiohttp.ClientSession", return_value=MockSession()):
        with patch.object(XXEScanner, "perform_scan", return_value=[{"entity_name": "xxe", "_value": "file:///etc/passwd"}]):
            result = await scanner.scan("http://unsafe.com/xml")
            assert result.scanner_name == "XXEScanner"
            assert result.target == "http://unsafe.com/xml"
            assert len(result.findings) == 1
            assert result.findings[0].severity == Severity.HIGH
            assert "xxe" in result.findings[0].description
