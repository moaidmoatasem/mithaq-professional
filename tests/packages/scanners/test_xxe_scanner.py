from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from cherenkov.core.base_scanner import Severity
from cherenkov.scanners.xxe_scanner import XXEScanner


@pytest.mark.asyncio
async def test_xxe_scanner_vulnerable():
    scanner = XXEScanner("xxe_scanner", "test scanner")

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
        result = await scanner.scan("http://vulnerable.com")

        assert result.target == "http://vulnerable.com"
        assert result.scanner_name == "xxe_scanner"
        assert len(result.findings) == 1

        finding = result.findings[0]
        assert finding.severity == Severity.HIGH
        assert finding.cwe == "CWE-611"
        assert "XML External Entity" in finding.title


@pytest.mark.asyncio
async def test_xxe_scanner_safe():
    scanner = XXEScanner("xxe_scanner", "test scanner")

    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, *args, **kwargs):
            return mock_response

    with patch("httpx.AsyncClient", return_value=MockClient()):
        result = await scanner.scan("http://safe.com")

        assert result.target == "http://safe.com"
        assert len(result.findings) == 0


@pytest.mark.asyncio
async def test_xxe_scanner_timeout():
    scanner = XXEScanner("xxe_scanner", "test scanner")

    import httpx

    with patch("httpx.AsyncClient", side_effect=httpx.RequestError("Error", request=MagicMock())):
        result = await scanner.scan("http://timeout.com")

        assert result.target == "http://timeout.com"
        assert len(result.findings) == 0
