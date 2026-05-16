import pytest
import httpx
from unittest.mock import AsyncMock, patch
from cherenkov.scanners.file_upload_scanner import FileUploadScanner
from cherenkov.core.base_scanner import Severity

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
    assert "Unsafe File Upload" in result.findings[0].title

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
