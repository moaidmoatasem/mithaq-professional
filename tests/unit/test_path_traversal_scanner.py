from unittest.mock import MagicMock, patch

import pytest
from cherenkov.core.base_scanner import Severity
from cherenkov.scanners.path_traversal_scanner import PathTraversalScanner


@pytest.mark.asyncio
async def test_path_traversal_positive():
    scanner = PathTraversalScanner()
    target = "http://example.com/api"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "root:x:0:0:root:/root:/bin/bash"

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, *args, **kwargs):
            return mock_response

    with patch("httpx.AsyncClient", return_value=MockClient()):
        result = await scanner.scan(target)

    assert result.target == target
    assert len(result.findings) == 1
    assert result.findings[0].severity == Severity.HIGH
    assert "Path Traversal" in result.findings[0].title


@pytest.mark.asyncio
async def test_path_traversal_negative():
    scanner = PathTraversalScanner()
    target = "http://example.com/api"

    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, *args, **kwargs):
            return mock_response

    with patch("httpx.AsyncClient", return_value=MockClient()):
        result = await scanner.scan(target)

    assert len(result.findings) == 0
