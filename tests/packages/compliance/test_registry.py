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


def test_owasptop10_2021_cwe_mappings_match_standard():
    """CWE→category mappings must follow the OWASP Top 10 2021 standard.

    XSS (CWE-79) is part of A03:2021-Injection (it left A07 after 2017).
    XXE (CWE-611) merged into A05:2021-Security Misconfiguration.
    Sensitive-info exposure (CWE-200) belongs to A01:2021-Broken Access Control.
    """
    fw = ComplianceRegistry.get("owasp2021")

    xxe = fw.map_finding({"title": "XXE", "severity": "HIGH", "cwe": "CWE-611"})
    assert "A05" in xxe.controls
    assert mapped_has_no_control(fw, "CWE-611", "A03")

    info = fw.map_finding({"title": "Info Exposure", "severity": "MEDIUM", "cwe": "CWE-200"})
    assert "A01" in info.controls
    assert mapped_has_no_control(fw, "CWE-200", "A09")

    xss = fw.map_finding({"title": "XSS", "severity": "HIGH", "cwe": "CWE-79"})
    assert "A03" in xss.controls
    assert mapped_has_no_control(fw, "CWE-79", "A07")


def mapped_has_no_control(fw, cwe: str, control_id: str) -> bool:
    """True when the control with id==control_id does not claim the given cwe."""
    return all(cwe not in c.cwe_list for c in fw.controls if c.id == control_id)


def test_owasptop10_all_known_cwe_pairs():
    """Every simplified CWE→OWASP 2021 pair must resolve correctly."""
    fw = ComplianceRegistry.get("owasp2021")
    known = {
        "CWE-284": "A01",
        "CWE-285": "A01",
        "CWE-639": "A01",
        "CWE-22": "A01",
        "CWE-200": "A01",
        "CWE-319": "A02",
        "CWE-311": "A02",
        "CWE-312": "A02",
        "CWE-327": "A02",
        "CWE-523": "A02",
        "CWE-89": "A03",
        "CWE-79": "A03",
        "CWE-78": "A03",
        "CWE-77": "A03",
        "CWE-693": "A04",
        "CWE-16": "A05",
        "CWE-749": "A05",
        "CWE-1021": "A05",
        "CWE-611": "A05",
        "CWE-306": "A07",
        "CWE-307": "A07",
        "CWE-308": "A07",
        "CWE-384": "A07",
        "CWE-778": "A09",
        "CWE-918": "A10",
    }
    for cwe, expected_control in known.items():
        result = fw.map_finding({"title": "test", "severity": "MEDIUM", "cwe": cwe})
        assert expected_control in result.controls, (
            f"{cwe} should map to {expected_control}, got {result.controls}"
        )


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
