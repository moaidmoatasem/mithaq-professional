"""Tests for the compliance framework registry and plugin auto-discovery."""

from __future__ import annotations

import pytest
from cherenkov.compliance import ComplianceRegistry
from cherenkov.compliance.base import ComplianceReport, MappedFinding


def test_egyfincsf_loads_and_maps_correctly():
    """Verify EgyFinCSF loads and maps CWE-89 correctly to PR-04."""
    fw = ComplianceRegistry.get("egyfincsf")
    assert fw is not None
    assert fw.framework_name == "EGY-FIN CSF"
    assert fw.framework_version == "1.0"
    assert fw.regulator == "Central Bank of Egypt (CBE)"

    finding = {
        "title": "SQL Injection",
        "severity": "CRITICAL",
        "cwe": "CWE-89",
        "remediation": "Use parameterized queries",
    }
    mapped = fw.map_finding(finding)
    assert isinstance(mapped, MappedFinding)
    assert mapped.finding_title == "SQL Injection"
    assert "PR-04" in mapped.controls
    assert mapped.domain == "Protect"
    assert mapped.remediation == "Use parameterized queries"


def test_samacsf_loads_and_maps_correctly():
    """Verify SamaCSF loads and maps CWE-319 correctly to 4.2."""
    fw = ComplianceRegistry.get("samacsf")
    assert fw is not None
    assert fw.framework_name == "SAMA CSF"
    assert fw.framework_version == "2.0"
    assert fw.regulator == "Saudi Central Bank (SAMA)"

    finding = {
        "title": "Cleartext Transmission",
        "severity": "HIGH",
        "cwe": "CWE-319",
        "remediation": "Use TLS",
    }
    mapped = fw.map_finding(finding)
    assert isinstance(mapped, MappedFinding)
    assert "4.2" in mapped.controls
    assert mapped.domain == "Protect"


def test_owasptop10_loads_and_maps_correctly():
    """Verify OWASPTop10 loads and maps CWE-79 correctly to A03."""
    fw = ComplianceRegistry.get("owasp2021")
    assert fw is not None
    assert fw.framework_name == "OWASP Top 10"
    assert fw.framework_version == "2021"

    finding = {
        "title": "Cross-Site Scripting",
        "severity": "HIGH",
        "cwe": "CWE-79",
        "remediation": "Escape output",
    }
    mapped = fw.map_finding(finding)
    assert isinstance(mapped, MappedFinding)
    assert "A03" in mapped.controls
    assert mapped.domain == "Injection"


def test_registry_list_frameworks():
    """Verify registry.list_frameworks() returns all 3 expected frameworks."""
    frameworks = ComplianceRegistry.list_frameworks()
    # Find our three target frameworks
    fw_ids = [fw["id"] for fw in frameworks]
    assert "egyfincsf" in fw_ids
    assert "samacsf" in fw_ids
    assert "owasp2021" in fw_ids

    # Find and verify specific metadata details
    egy = next(f for f in frameworks if f["id"] == "egyfincsf")
    assert egy["name"] == "EGY-FIN CSF"
    assert egy["controls"] == 10

    sama = next(f for f in frameworks if f["id"] == "samacsf")
    assert sama["name"] == "SAMA CSF"
    assert sama["controls"] == 10

    owasp = next(f for f in frameworks if f["id"] == "owasp2021")
    assert owasp["name"] == "OWASP Top 10"
    assert owasp["controls"] == 10


def test_unknown_framework_raises_value_error():
    """Verify registry.generate_report with unknown framework raises ValueError."""
    findings = [{"cwe": "CWE-89", "title": "SQLi"}]
    with pytest.raises(ValueError, match="Unknown framework: unknown_fw"):
        ComplianceRegistry.generate_report("unknown_fw", findings, "scan-123")


def test_generate_report_success():
    """Verify standard ComplianceReport generation."""
    findings = [
        {"title": "SQLi", "cwe": "CWE-89", "severity": "CRITICAL", "remediation": "Fix"},
        {"title": "XSS", "cwe": "CWE-79", "severity": "HIGH", "remediation": "Fix"},
        {"title": "Strange Vuln", "cwe": "CWE-999", "severity": "LOW", "remediation": "Fix"},
    ]
    report = ComplianceRegistry.generate_report("egyfincsf", findings, "scan-123")
    assert isinstance(report, ComplianceReport)
    assert report.scan_id == "scan-123"
    assert report.framework_id == "egyfincsf"
    assert report.controls_total == 10
    assert report.findings_mapped == 2
    assert report.findings_unmapped == 1
    assert len(report.mapped_findings) == 3
