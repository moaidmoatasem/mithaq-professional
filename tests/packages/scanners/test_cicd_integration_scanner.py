from unittest.mock import MagicMock, patch

import pytest
import httpx
from cherenkov.core.base_scanner import Severity
from cherenkov.scanners.cicd_integration_scanner import CICDIntegrationScanner


@pytest.mark.asyncio
async def test_cicd_scanner_vulnerable():
    scanner = CICDIntegrationScanner("cicd_integration_scanner", "test scanner")

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.text = "[core]\nrepositoryformatversion=0"

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, url, **kwargs):
            return mock_response

    with patch("httpx.AsyncClient", return_value=MockClient()):
        result = await scanner.scan("http://vulnerable.local")

        assert result.target == "http://vulnerable.local"
        assert result.scanner_name == "cicd_integration_scanner"
        assert len(result.findings) > 0

        finding = result.findings[0]
        assert finding.severity == Severity.HIGH
        assert finding.cwe == "CWE-538"
        assert "Git Configuration" in finding.title


@pytest.mark.asyncio
async def test_cicd_scanner_safe():
    scanner = CICDIntegrationScanner("cicd_integration_scanner", "test scanner")

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 404
    mock_response.text = "Not Found"

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, url, **kwargs):
            return mock_response

    with patch("httpx.AsyncClient", return_value=MockClient()):
        result = await scanner.scan("http://safe.local")

        assert result.target == "http://safe.local"
        assert len(result.findings) == 0


@pytest.mark.asyncio
async def test_cicd_scanner_timeout():
    scanner = CICDIntegrationScanner("cicd_integration_scanner", "test scanner")

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, url, **kwargs):
            raise httpx.RequestError("Network error")

    with patch("httpx.AsyncClient", return_value=MockClient()):
        result = await scanner.scan("http://timeout.local")

        assert result.target == "http://timeout.local"
        assert len(result.findings) == 0
