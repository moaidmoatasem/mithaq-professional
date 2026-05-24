"""Unit tests for CICDIntegrationScanner."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from cherenkov.scanners.cicd_integration_scanner import CICDIntegrationScanner


@pytest.mark.asyncio
async def test_returns_scan_result_structure():
    scanner = CICDIntegrationScanner()
    with patch.object(scanner, "_http_request", new_callable=AsyncMock) as mock_req:
        mock_req.side_effect = Exception("timeout")
        result = await scanner.scan("http://target.example.com")

    assert result.scanner_name == "cicd_integration"
    assert result.target == "http://target.example.com"
    assert isinstance(result.findings, list)
    assert result.duration_ms >= 0


@pytest.mark.asyncio
async def test_detects_exposed_env_file():
    scanner = CICDIntegrationScanner()

    async def fake_request(url, timeout):
        m = MagicMock()
        m.status_code = 200 if url.endswith("/.env") else 404
        return m

    with patch.object(scanner, "_http_request", side_effect=fake_request):
        result = await scanner.scan("http://target.example.com")

    assert any(".env" in f.title for f in result.findings)
    critical = [f for f in result.findings if f.severity.value == "CRITICAL"]
    assert critical


@pytest.mark.asyncio
async def test_detects_dockerfile():
    scanner = CICDIntegrationScanner()

    async def fake_request(url, timeout):
        m = MagicMock()
        m.status_code = 200 if url.endswith("/Dockerfile") else 404
        return m

    with patch.object(scanner, "_http_request", side_effect=fake_request):
        result = await scanner.scan("http://target.example.com")

    assert any("Dockerfile" in f.title for f in result.findings)


@pytest.mark.asyncio
async def test_no_findings_on_clean_target():
    scanner = CICDIntegrationScanner()

    async def fake_request(url, timeout):
        m = MagicMock()
        m.status_code = 404
        return m

    with patch.object(scanner, "_http_request", side_effect=fake_request):
        result = await scanner.scan("http://target.example.com")

    assert result.findings == []


def test_scanner_metadata():
    s = CICDIntegrationScanner()
    assert s.name == "cicd_integration"
    assert "ci" in s.description.lower() or "pipeline" in s.description.lower()
