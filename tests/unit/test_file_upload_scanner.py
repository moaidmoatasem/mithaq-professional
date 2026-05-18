from unittest.mock import AsyncMock, patch

import httpx
import pytest
from cherenkov.core.base_scanner import Severity

FileUploadScanner = pytest.importorskip(
    "cherenkov.scanners.file_upload_scanner",
    reason="file_upload_scanner not yet graduated — issue #178",
).FileUploadScanner

pytestmark = pytest.mark.ai_generated


@pytest.mark.asyncio
async def test_file_upload_positive():
    scanner = FileUploadScanner()
    target = "http://example.com"

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = "File shell.php uploaded successfully"

    with patch("httpx.AsyncClient.post", return_value=mock_response):
        result = await scanner.scan(target)

    assert len(result.findings) == 1
    assert result.findings[0].severity == Severity.HIGH
    assert "Unrestricted File Upload" in result.findings[0].title



@pytest.mark.asyncio
async def test_file_upload_negative():
    scanner = FileUploadScanner()
    target = "http://example.com"

    mock_response = AsyncMock()
    mock_response.status_code = 403
    mock_response.text = "File type not allowed"

    with patch("httpx.AsyncClient.post", return_value=mock_response):
        result = await scanner.scan(target)

    assert len(result.findings) == 0
