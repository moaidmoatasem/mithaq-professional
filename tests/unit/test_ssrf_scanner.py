import pytest
import httpx
from unittest.mock import AsyncMock, patch
from cherenkov.scanners.ssrf_scanner import SSRFScanner, _find_url_params, _inject_canary
from cherenkov.core.base_scanner import Severity


@pytest.mark.asyncio
async def test_ssrf_positive_indicator_in_response():
    """URL param triggers a server fetch; response contains 'connection refused' → finding."""
    scanner = SSRFScanner()
    target = "http://example.com/fetch?url=http://safe.example.com"

    call_count = 0

    async def mock_get(url, **kwargs):
        nonlocal call_count
        call_count += 1
        resp = AsyncMock()
        resp.status_code = 200
        if call_count == 1:
            # Baseline
            resp.text = "Welcome page"
        else:
            # Probe — server echoed SSRF artifact
            resp.text = "Error: connection refused to 127.0.0.1:80"
        return resp

    with patch("httpx.AsyncClient.get", side_effect=mock_get):
        result = await scanner.scan(target)

    assert len(result.findings) == 1
    finding = result.findings[0]
    assert finding.severity == Severity.HIGH
    assert "SSRF" in finding.title
    assert finding.cwe == "CWE-918"


@pytest.mark.asyncio
async def test_ssrf_negative_no_indicator():
    """Server returns 200 with no SSRF artefacts → no finding."""
    scanner = SSRFScanner()
    target = "http://example.com/fetch?url=http://safe.example.com"

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = "Fetched content rendered here"

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await scanner.scan(target)

    assert len(result.findings) == 0


@pytest.mark.asyncio
async def test_ssrf_indicator_present_in_baseline_is_ignored():
    """
    If the baseline response already contains an SSRF keyword, it must not
    trigger a false positive when the probe response also contains it.
    """
    scanner = SSRFScanner()
    target = "http://example.com/fetch?url=http://safe.example.com"

    async def mock_get(url, **kwargs):
        resp = AsyncMock()
        resp.status_code = 200
        # Both baseline and probe contain the same text
        resp.text = "connection refused — this site is unavailable"
        return resp

    with patch("httpx.AsyncClient.get", side_effect=mock_get):
        result = await scanner.scan(target)

    assert len(result.findings) == 0


@pytest.mark.asyncio
async def test_ssrf_no_url_params_uses_synthetic():
    """URL without params still probes via synthetic 'url' parameter."""
    scanner = SSRFScanner()
    target = "http://example.com/api"

    called_urls: list[str] = []

    async def capture(url, **kwargs):
        called_urls.append(str(url))
        resp = AsyncMock()
        resp.status_code = 200
        resp.text = "OK"
        return resp

    with patch("httpx.AsyncClient.get", side_effect=capture):
        await scanner.scan(target)

    assert any("url=" in u for u in called_urls)


@pytest.mark.asyncio
async def test_ssrf_network_error_degrades_gracefully():
    scanner = SSRFScanner()
    target = "http://unreachable.local/fetch?url=x"

    with patch("httpx.AsyncClient.get", side_effect=httpx.ConnectError("refused")):
        result = await scanner.scan(target)

    assert result.status == "completed"
    assert len(result.findings) == 0


def test_find_url_params_known_names():
    params = _find_url_params("http://example.com/redir?url=http://x.com&src=y")
    assert "url" in params
    assert "src" in params


def test_find_url_params_unknown_fallback():
    """Unknown param names: return all params as fallback."""
    params = _find_url_params("http://example.com/?foo=1&bar=2")
    assert set(params) == {"foo", "bar"}


def test_inject_canary_replaces_param():
    result = _inject_canary("http://example.com/?url=http://safe.com", "url", "http://127.0.0.1/")
    assert "url=http" in result
    assert "127.0.0.1" in result
