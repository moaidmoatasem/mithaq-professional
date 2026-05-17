import pytest
import httpx
from unittest.mock import AsyncMock, patch
from cherenkov.scanners.xxe_scanner import XXEScanner
from cherenkov.core.base_scanner import Severity

@pytest.mark.asyncio
async def test_xxe_scanner_positive():
    scanner = XXEScanner()
    target = "http://example.com/api"
    
    # Mock httpx.AsyncClient.post
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = "root:x:0:0:root:/root:/bin/bash"
    
    with patch("httpx.AsyncClient.post", return_value=mock_response):
        result = await scanner.scan(target)
        
    assert result.target == target
    assert len(result.findings) == 1
    assert result.findings[0].severity == Severity.HIGH
    assert "XXE" in result.findings[0].title

@pytest.mark.asyncio
async def test_xxe_scanner_negative():
    scanner = XXEScanner()
    target = "http://example.com/api"
    
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = "OK"
    
    with patch("httpx.AsyncClient.post", return_value=mock_response):
        result = await scanner.scan(target)
        
    assert len(result.findings) == 0

@pytest.mark.asyncio
async def test_xxe_scanner_timeout():
    scanner = XXEScanner()
    target = "http://example.com/api"
    
    with patch("httpx.AsyncClient.post", side_effect=httpx.TimeoutException("Timeout")):
        result = await scanner.scan(target)
        
    assert len(result.findings) == 0
    assert result.status == "completed"
