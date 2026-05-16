import pytest
import httpx
from unittest.mock import AsyncMock, patch
from cherenkov.scanners.path_traversal_scanner import PathTraversalScanner
from cherenkov.core.base_scanner import Severity

@pytest.mark.asyncio
async def test_path_traversal_positive():
    scanner = PathTraversalScanner()
    target = "http://example.com/api"
    
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = "root:x:0:0:root:/root:/bin/bash"
    
    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await scanner.scan(target)
        
    assert result.target == target
    assert len(result.findings) == 1
    assert result.findings[0].severity == Severity.HIGH
    assert "Path Traversal" in result.findings[0].title

@pytest.mark.asyncio
async def test_path_traversal_negative():
    scanner = PathTraversalScanner()
    target = "http://example.com/api"
    
    mock_response = AsyncMock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    
    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await scanner.scan(target)
        
    assert len(result.findings) == 0
