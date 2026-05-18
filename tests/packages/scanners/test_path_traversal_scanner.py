from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from cherenkov.core.base_scanner import Severity
from cherenkov.scanners.path_traversal_scanner import PathTraversalScanner


@pytest.mark.asyncio
async def test_path_traversal_vulnerable():
    scanner = PathTraversalScanner("path_traversal", "test scanner")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "root:x:0:0:root:/root:/bin/bash"

    class MockClient:
        async def __aenter__(self): return self
        async def __aexit__(self, *args): pass
        async def get(self, *args, **kwargs): return mock_response

    with patch("httpx.AsyncClient", return_value=MockClient()):
        result = await scanner.scan("http://vulnerable.com/download?file=")

        assert result.target == "http://vulnerable.com/download?file="
        assert len(result.findings) == 1

        finding = result.findings[0]
        assert finding.severity == Severity.HIGH
        assert finding.cwe == "CWE-22"
        assert "Path Traversal" in finding.title

@pytest.mark.asyncio
async def test_path_traversal_safe():
    scanner = PathTraversalScanner("path_traversal", "test scanner")

    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.text = "Forbidden"

    class MockClient:
        async def __aenter__(self): return self
        async def __aexit__(self, *args): pass
        async def get(self, *args, **kwargs): return mock_response

    with patch("httpx.AsyncClient", return_value=MockClient()):
        result = await scanner.scan("http://safe.com/download?file=")

        assert len(result.findings) == 0

@pytest.mark.asyncio
async def test_path_traversal_timeout():
    scanner = PathTraversalScanner("path_traversal", "test scanner")

    import httpx
    with patch("httpx.AsyncClient", side_effect=httpx.RequestError("Error", request=MagicMock())):
        result = await scanner.scan("http://timeout.com/download?file=")

        assert len(result.findings) == 0
