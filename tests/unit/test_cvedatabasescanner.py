import pytest
from unittest.mock import patch, MagicMock

from cherenkov.autonomous_generated.scanners.cvedatabasescanner import CVEDatabaseScanner
from cherenkov.core.base_scanner import Severity

@pytest.mark.asyncio
async def test_cvedatabasescanner_safe():
    scanner = CVEDatabaseScanner()

    class MockResponse:
        status = 200
        async def json(self):
            return {"results": []}
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
        result = await scanner.scan("safe-package")
        assert result.scanner_name == "CVEDatabaseScanner"
        assert result.target == "safe-package"
        assert len(result.findings) == 0

@pytest.mark.asyncio
async def test_cvedatabasescanner_unsafe():
    scanner = CVEDatabaseScanner()

    class MockResponse:
        status = 200
        async def json(self):
            return {"results": [{"cve": "CVE-2023-1234", "details": "bad vuln"}]}
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
        result = await scanner.scan("unsafe-package")
        assert result.scanner_name == "CVEDatabaseScanner"
        assert result.target == "unsafe-package"
        assert len(result.findings) == 1
        assert result.findings[0].severity == Severity.HIGH
        assert "CVE-2023-1234" in result.findings[0].description
