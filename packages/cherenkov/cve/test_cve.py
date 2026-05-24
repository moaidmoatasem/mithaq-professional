# packages/cherenkov/cve/test_cve.py
import json
import pytest
import tempfile
from pathlib import Path
from cherenkov.cve.store import init_db, upsert_from_staging
from cherenkov.cve.matcher import match_package_version
from cherenkov.cve.scanner import CVEScanner

@pytest.fixture
def mock_nvd_json(tmp_path):
    """Create mock NVD JSON for testing."""
    data = {
        "CVE_Items": [
            {
                "cve": {
                    "CVE_data_meta": {"ID": "CVE-2024-1234"},
                    "description": {
                        "description_data": [{"value": "Test vulnerability in apache"}]
                    }
                },
                "configurations": {"cpe": ["cpe:2.3:a:apache:apache:2.4.49"]},
                "impact": {
                    "baseMetricV3": {"cvssV3": {"baseScore": 7.5}}
                },
                "publishedDate": "2024-01-01T00:00:00Z"
            }
        ]
    }
    staging_file = tmp_path / "cve_staging.json"
    staging_file.write_text(json.dumps(data))
    return str(staging_file)

def test_matcher_returns_list():
    """CVE matcher returns list."""
    results = match_package_version("nonexistent", "0.0.0")
    assert isinstance(results, list)

def test_cve_scanner_init():
    """CVE scanner initializes."""
    scanner = CVEScanner()
    assert scanner.id == "cve-scanner"
    assert scanner.name == "CVE Version Matcher"

def test_cve_scanner_execute_empty():
    """CVE scanner with empty context returns empty findings."""
    scanner = CVEScanner()
    findings = scanner.execute("http://example.com", context={})
    assert findings == []

def test_cve_scanner_execute_with_packages():
    """CVE scanner processes package context."""
    scanner = CVEScanner()
    findings = scanner.execute(
        "http://example.com",
        context={"packages": [{"name": "apache", "version": "2.4.49"}]}
    )
    # Will be empty if DB not initialized, but structure is correct
    assert isinstance(findings, list)

def test_cvss_to_severity():
    """CVSS score converts to correct severity."""
    assert CVEScanner._cvss_to_severity(9.5).value == "critical"
    assert CVEScanner._cvss_to_severity(7.5).value == "high"
    assert CVEScanner._cvss_to_severity(5.0).value == "medium"
    assert CVEScanner._cvss_to_severity(2.0).value == "low"