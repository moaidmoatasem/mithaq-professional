import pytest
import httpx
from unittest.mock import AsyncMock, patch
from cherenkov.scanners.xss_scanner import XSSScanner
from cherenkov.core.base_scanner import Severity


@pytest.mark.asyncio
async def test_xss_positive_reflected_payload():
    """Server echoes raw script tag → reflected XSS finding."""
    scanner = XSSScanner()
    target = "http://example.com/search?q=hello"

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = "Results for: <script>cherenkov_xss</script>"

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await scanner.scan(target)

    assert len(result.findings) == 1
    finding = result.findings[0]
    assert finding.severity == Severity.HIGH
    assert "XSS" in finding.title
    assert finding.cwe == "CWE-79"


@pytest.mark.asyncio
async def test_xss_positive_onerror_attribute():
    """Server reflects an onerror attribute → XSS finding via second probe."""
    scanner = XSSScanner()
    target = "http://example.com/page?name=world"

    call_count = 0

    async def side_effect(url, **kwargs):
        nonlocal call_count
        call_count += 1
        resp = AsyncMock()
        resp.status_code = 200
        # Second probe carries the img onerror payload
        if call_count == 2:
            resp.text = 'Hello <img src=x onerror="cherenkov_xss"> there'
        else:
            resp.text = "No reflection here"
        return resp

    with patch("httpx.AsyncClient.get", side_effect=side_effect):
        result = await scanner.scan(target)

    assert len(result.findings) == 1
    assert result.findings[0].cwe == "CWE-79"


@pytest.mark.asyncio
async def test_xss_negative_encoded_response():
    """Server HTML-encodes the payload → no finding."""
    scanner = XSSScanner()
    target = "http://example.com/search?q=test"

    mock_response = AsyncMock()
    mock_response.status_code = 200
    # Properly encoded — & lt; etc. — marker not present raw
    mock_response.text = "Results: &lt;script&gt;cherenkov_xss&lt;/script&gt;"

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await scanner.scan(target)

    assert len(result.findings) == 0


@pytest.mark.asyncio
async def test_xss_negative_404_response():
    """Server returns 404 even if body contains the probe → no finding."""
    scanner = XSSScanner()
    target = "http://example.com/search?q=test"

    mock_response = AsyncMock()
    mock_response.status_code = 404
    mock_response.text = "<script>cherenkov_xss</script> not found"

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await scanner.scan(target)

    assert len(result.findings) == 0


@pytest.mark.asyncio
async def test_xss_no_params_injects_synthetic():
    """URL without query params probes via synthetic search= parameter."""
    scanner = XSSScanner()
    target = "http://example.com/page"

    called_urls: list[str] = []

    async def capture(url, **kwargs):
        called_urls.append(str(url))
        resp = AsyncMock()
        resp.status_code = 200
        resp.text = "clean page"
        return resp

    with patch("httpx.AsyncClient.get", side_effect=capture):
        await scanner.scan(target)

    assert any("search=" in u for u in called_urls)


@pytest.mark.asyncio
async def test_xss_network_error_degrades_gracefully():
    scanner = XSSScanner()
    target = "http://unreachable.local/?q=x"

    with patch("httpx.AsyncClient.get", side_effect=httpx.ConnectError("refused")):
        result = await scanner.scan(target)

    assert result.status == "completed"
    assert len(result.findings) == 0


@pytest.mark.asyncio
async def test_xss_stops_after_first_finding():
    """Scanner breaks out after confirming one finding — no duplicate reports."""
    scanner = XSSScanner()
    target = "http://example.com/search?a=1&b=2"

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = "<script>cherenkov_xss</script>"

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await scanner.scan(target)

    assert len(result.findings) == 1
