import json
from unittest.mock import mock_open, patch

import pytest
from cherenkov.core.base_scanner import Severity
from cherenkov.scanners.cve_database_scanner import DEFAULT_CVES, CVEDatabaseScanner


def test_cve_scanner_basic_init():
    """Verify that CVEDatabaseScanner initializes with correct default metadata."""
    scanner = CVEDatabaseScanner()
    assert scanner.name == "CVEDatabaseScanner"
    assert "local" in scanner.description.lower()
    assert scanner.version == "1.0.0"
    assert len(scanner.cves) > 0


def test_cve_scanner_legacy_get_vulnerabilities():
    """Verify that get_vulnerabilities method works as expected (legacy interface)."""
    scanner = CVEDatabaseScanner()

    # All CVEs
    vulns = scanner.get_vulnerabilities(max_results=5)
    assert len(vulns) <= 5

    # Filtered by severity
    critical_vulns = scanner.get_vulnerabilities(severity="CRITICAL")
    for vuln in critical_vulns:
        assert vuln["severity"].upper() == "CRITICAL"

    # Invalid severity raises ValueError
    with pytest.raises(ValueError, match="Valid severities are"):
        scanner.get_vulnerabilities(severity="SUPER_BAD")

    # Too many results raises ValueError
    with pytest.raises(ValueError, match="Max results cannot exceed 100"):
        scanner.get_vulnerabilities(max_results=101)


@pytest.mark.asyncio
async def test_cve_scanner_vulnerable_targets():
    """Verify that scanning a target containing a vulnerable component returns correct findings."""
    scanner = CVEDatabaseScanner()

    # Target containing "xz-utils"
    result = await scanner.scan("http://internal-xz-utils-server.local")
    assert result.status == "completed"
    assert len(result.findings) == 1
    finding = result.findings[0]
    assert "CVE-2024-3094" in finding.title
    assert finding.severity == Severity.CRITICAL
    assert finding.cwe == "CWE-506"
    assert "unauthorized SSH access" in finding.description
    assert "Downgrade xz-utils" in finding.remediation

    # Target containing "runc"
    result_runc = await scanner.scan("runc-container-host")
    assert result_runc.status == "completed"
    assert len(result_runc.findings) == 1
    assert "CVE-2024-21626" in result_runc.findings[0].title
    assert result_runc.findings[0].severity == Severity.CRITICAL


@pytest.mark.asyncio
async def test_cve_scanner_clean_target():
    """Verify that a target without any vulnerable components returns no findings."""
    scanner = CVEDatabaseScanner()

    result = await scanner.scan("http://secure-django-app.local")
    assert result.status == "completed"
    assert len(result.findings) == 0


@pytest.mark.asyncio
async def test_cve_scanner_invalid_target():
    """Verify that invalid/unsafe target formats are rejected immediately with 'failed' status to prevent injection."""
    scanner = CVEDatabaseScanner()

    unsafe_targets = [
        "127.0.0.1; rm -rf /",
        "example.com && ping 8.8.8.8",
        "$(whoami).evil.com",
        "my_host/some/path/with/spaces ",
    ]

    for target in unsafe_targets:
        result = await scanner.scan(target)
        assert result.status == "failed"
        assert len(result.findings) == 0


@pytest.mark.asyncio
async def test_cve_scanner_airgap_enforcement():
    """Verify that the scanner makes absolutely no outbound network calls during its execution (MEISSNER air-gap)."""
    scanner = CVEDatabaseScanner()

    # Using patch to monitor requests and httpx packages
    with patch("requests.get") as mock_req_get, patch("httpx.get") as mock_httpx_get:
        result = await scanner.scan("http://runc-vulnerable.local")
        assert result.status == "completed"
        assert len(result.findings) == 1

        # Ensure no network requests were triggered
        mock_req_get.assert_not_called()
        mock_httpx_get.assert_not_called()


def test_cve_scanner_json_load_fallback():
    """Verify that if the cves.json feed is missing or corrupt, it gracefully falls back to python embedded defaults."""
    # Scenario 1: Path does not exist
    with patch("pathlib.Path.exists", return_value=False):
        scanner = CVEDatabaseScanner()
        assert len(scanner.cves) == len(DEFAULT_CVES)
        assert scanner.cves[0]["cve_id"] == DEFAULT_CVES[0]["cve_id"]

    # Scenario 2: Corrupt JSON file raises exception
    with patch("pathlib.Path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data="INVALID JSON")):
        scanner = CVEDatabaseScanner()
        assert len(scanner.cves) == len(DEFAULT_CVES)
        assert scanner.cves[0]["cve_id"] == DEFAULT_CVES[0]["cve_id"]
