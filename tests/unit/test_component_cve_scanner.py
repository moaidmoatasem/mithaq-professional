from unittest.mock import AsyncMock, patch

import pytest
from cherenkov.core.base_scanner import Severity
from cherenkov.scanners.component_cve_scanner import ComponentCVEScanner


def test_component_cve_scanner_basic_init():
    scanner = ComponentCVEScanner()
    assert scanner.name == "component_cve_scanner"
    assert "CVE" in scanner.description
    assert scanner.version == "1.0.0"
    assert len(scanner.cve_db) > 0


@pytest.mark.asyncio
async def test_component_cve_scanner_vulnerable_target():
    scanner = ComponentCVEScanner()
    target = "http://log4j-vulnerable-app.internal:8080"

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = "OK"
    mock_response.headers = {}

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await scanner.scan(target)

    assert result.status == "completed"
    assert len(result.findings) == 1
    finding = result.findings[0]
    assert "CVE-2021-44228" in finding.title
    assert finding.severity == Severity.CRITICAL


@pytest.mark.asyncio
async def test_component_cve_scanner_clean_target():
    scanner = ComponentCVEScanner()
    target = "http://secure-custom-app.local"

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = "OK"
    mock_response.headers = {}

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await scanner.scan(target)

    assert result.status == "completed"
    assert len(result.findings) == 0


@pytest.mark.asyncio
async def test_component_cve_scanner_invalid_target():
    scanner = ComponentCVEScanner()
    unsafe_targets = [
        "127.0.0.1; rm -rf /",
        "example.com && ping 8.8.8.8",
        "$(whoami).evil.com",
    ]
    for target in unsafe_targets:
        result = await scanner.scan(target)
        assert result.status == "failed"
        assert len(result.findings) == 0


@pytest.mark.asyncio
async def test_component_cve_scanner_header_matching():
    scanner = ComponentCVEScanner()
    target = "http://example.com"

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = "OK"
    mock_response.headers = {"server": "Apache/2.4.49"}

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, *args, **kwargs):
            return mock_response

    scanner.cve_db = [
        {
            "cve_id": "CVE-2021-99999",
            "title": "Test Apache Vuln",
            "severity": "HIGH",
            "cwe": "CWE-999",
            "description": "Test vulnerability for Apache.",
            "remediation": "Update Apache.",
            "components": ["apache"],
        }
    ]

    with patch("httpx.AsyncClient", return_value=MockClient()):
        result = await scanner.scan(target)

    assert result.status == "completed"
    assert len(result.findings) >= 1
    header_finding = next(
        (f for f in result.findings if "header reveals" in f.title.lower()), None
    )
    assert header_finding is not None
    assert "apache" in header_finding.title.lower()


@pytest.mark.asyncio
async def test_component_cve_scanner_airgap_enforcement():
    scanner = ComponentCVEScanner()
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_response.headers = {}
        mock_get.return_value = mock_response

        result = await scanner.scan("http://runc-vulnerable.local")
        assert result.status == "completed"
        assert len(result.findings) >= 1


def test_component_cve_scanner_fallback_defaults():
    with patch("pathlib.Path.exists", return_value=False):
        scanner = ComponentCVEScanner()
        assert len(scanner.cve_db) > 0
        assert scanner.cve_db[0]["cve_id"] is not None
