from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from cherenkov.core.base_scanner import Severity

_mod = pytest.importorskip(
    "cherenkov.scanners.file_upload_scanner",
    reason="file_upload_scanner not yet graduated — issue #178",
)
FileUploadScanner = _mod.FileUploadScanner

pytestmark = pytest.mark.ai_generated


@pytest.mark.asyncio
async def test_file_upload_vulnerable():
    scanner = FileUploadScanner("file_upload", "test scanner")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "File uploaded successfully: test_shell.php"

    class MockClient:
        async def __aenter__(self): return self
        async def __aexit__(self, *args): pass
        async def post(self, *args, **kwargs): return mock_response

    with patch("httpx.AsyncClient", return_value=MockClient()):
        result = await scanner.scan("http://vulnerable.com/upload")

        assert result.target == "http://vulnerable.com/upload"
        assert len(result.findings) == 1

        finding = result.findings[0]
        assert finding.severity == Severity.HIGH
        assert finding.cwe == "CWE-434"
        assert "Unrestricted File Upload" in finding.title


@pytest.mark.asyncio
async def test_file_upload_safe():
    scanner = FileUploadScanner("file_upload", "test scanner")

    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.text = "File type not allowed"

    class MockClient:
        async def __aenter__(self): return self
        async def __aexit__(self, *args): pass
        async def post(self, *args, **kwargs): return mock_response

    with patch("httpx.AsyncClient", return_value=MockClient()):
        result = await scanner.scan("http://safe.com/upload")

        assert len(result.findings) == 0


@pytest.mark.asyncio
async def test_file_upload_timeout():
    scanner = FileUploadScanner("file_upload", "test scanner")

    import httpx
    with patch("httpx.AsyncClient", side_effect=httpx.RequestError("Error", request=MagicMock())):
        result = await scanner.scan("http://timeout.com/upload")

        assert len(result.findings) == 0
