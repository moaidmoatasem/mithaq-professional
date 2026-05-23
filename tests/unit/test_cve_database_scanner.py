"""Unit tests for CVEDatabaseScanner."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from cherenkov.scanners.cve_database_scanner import CVEDatabaseScanner


@pytest.mark.asyncio
async def test_returns_scan_result_structure():
    scanner = CVEDatabaseScanner()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = {}

    with patch.object(scanner, "_http_request", new_callable=AsyncMock, return_value=mock_resp):
        result = await scanner.scan("http://target.example.com")

    assert result.scanner_name == "cve_database"
    assert result.target == "http://target.example.com"
    assert isinstance(result.findings, list)
    assert result.duration_ms >= 0


@pytest.mark.asyncio
async def test_detects_eol_apache():
    scanner = CVEDatabaseScanner()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = {"server": "Apache/1.3.42 (Unix)"}

    with patch.object(scanner, "_http_request", new_callable=AsyncMock, return_value=mock_resp):
        result = await scanner.scan("http://target.example.com")

    assert any("Apache" in f.title for f in result.findings)
    assert result.findings[0].severity.value == "HIGH"


@pytest.mark.asyncio
async def test_detects_eol_php():
    scanner = CVEDatabaseScanner()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = {"x-powered-by": "PHP/5.6.40"}

    with patch.object(scanner, "_http_request", new_callable=AsyncMock, return_value=mock_resp):
        result = await scanner.scan("http://target.example.com")

    assert any("PHP" in f.title for f in result.findings)
    assert result.findings[0].severity.value == "CRITICAL"


@pytest.mark.asyncio
async def test_no_findings_on_clean_headers():
    scanner = CVEDatabaseScanner()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = {"content-type": "text/html"}

    with patch.object(scanner, "_http_request", new_callable=AsyncMock, return_value=mock_resp):
        result = await scanner.scan("http://target.example.com")

    assert result.findings == []


@pytest.mark.asyncio
async def test_error_returns_error_status():
    scanner = CVEDatabaseScanner()
    with patch.object(scanner, "_http_request", new_callable=AsyncMock, side_effect=Exception("conn")):
        result = await scanner.scan("http://target.example.com")

    assert result.status == "error"
    assert result.findings == []


def test_scanner_metadata():
    s = CVEDatabaseScanner()
    assert s.name == "cve_database"
    assert "version" in s.description.lower()
