import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from cherenkov.scanners.sql_injection_scanner import SQLInjectionScanner, _inject_into_params
from cherenkov.core.base_scanner import Severity


@pytest.mark.asyncio
async def test_sqli_positive_error_signature():
    """Server responds with a MySQL error string → finding reported."""
    scanner = SQLInjectionScanner()
    target = "http://example.com/search?q=test"

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = "You have an error in your SQL syntax near 'q='' at line 1"

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await scanner.scan(target)

    assert len(result.findings) == 1
    finding = result.findings[0]
    assert finding.severity == Severity.CRITICAL
    assert "SQL Injection" in finding.title
    assert finding.cwe == "CWE-89"


@pytest.mark.asyncio
async def test_sqli_negative_clean_response():
    """Server returns 200 with no SQL error strings → no finding."""
    scanner = SQLInjectionScanner()
    target = "http://example.com/search?q=test"

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = "Search results for your query"

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await scanner.scan(target)

    assert len(result.findings) == 0


@pytest.mark.asyncio
async def test_sqli_negative_non_200():
    """Server returns 500 even with SQL error text → no finding (error not exploitable via 200)."""
    scanner = SQLInjectionScanner()
    target = "http://example.com/api?id=1"

    mock_response = AsyncMock()
    mock_response.status_code = 500
    mock_response.text = "ODBC SQL Server Driver: syntax error"

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await scanner.scan(target)

    assert len(result.findings) == 0


@pytest.mark.asyncio
async def test_sqli_no_params_injects_synthetic():
    """URL with no query params still probes via synthetic 'id' parameter."""
    scanner = SQLInjectionScanner()
    target = "http://example.com/api"

    called_urls: list[str] = []

    async def capture_get(url, **kwargs):
        called_urls.append(str(url))
        resp = AsyncMock()
        resp.status_code = 200
        resp.text = "OK"
        return resp

    with patch("httpx.AsyncClient.get", side_effect=capture_get):
        await scanner.scan(target)

    assert any("id=" in u for u in called_urls), f"Expected synthetic id param in {called_urls}"


@pytest.mark.asyncio
async def test_sqli_network_error_degrades_gracefully():
    """Request errors during probing do not raise; result has 0 findings."""
    scanner = SQLInjectionScanner()
    target = "http://unreachable.local/search?q=x"

    with patch("httpx.AsyncClient.get", side_effect=httpx.ConnectError("refused")):
        result = await scanner.scan(target)

    assert result.status == "completed"
    assert len(result.findings) == 0


def test_inject_into_params_single_param():
    urls = _inject_into_params("http://example.com/page?id=5", "' OR 1=1--")
    assert len(urls) == 1
    assert "id=" in urls[0]
    assert "OR+1%3D1" in urls[0] or "OR" in urls[0]


def test_inject_into_params_no_params():
    urls = _inject_into_params("http://example.com/page", "payload")
    assert len(urls) == 1
    assert "id=payload" in urls[0]


def test_inject_into_params_multiple_params():
    urls = _inject_into_params("http://example.com/search?q=a&cat=b", "x")
    assert len(urls) == 2
