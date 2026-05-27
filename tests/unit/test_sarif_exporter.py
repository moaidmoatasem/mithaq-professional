import pytest
from cherenkov.compliance.reports import SARIFExporter
from cherenkov.compliance.mapper import ComplianceMapper
from cherenkov.core.base_scanner import ScanResult, Finding, Severity

def test_sarif_exporter_basic():
    finding = Finding(
        title="XSS Finding",
        severity=Severity.HIGH,
        description="Reflected XSS on /search",
        cwe="CWE-79",
        remediation="Sanitize inputs"
    )
    result = ScanResult(
        target="http://example.com",
        scanner_name="TestScanner",
        findings=[finding],
        status="completed"
    )
    
    exporter = SARIFExporter(result, compliance_mapper=ComplianceMapper(), chk_id="CHK-123")
    sarif = exporter.generate()
    
    assert sarif["version"] == "2.1.0"
    assert len(sarif["runs"]) == 1
    run = sarif["runs"][0]
    assert run["tool"]["driver"]["name"] == "Cherenkov Scanner"
    assert len(run["results"]) == 1
    
    res = run["results"][0]
    assert res["ruleId"] == "CWE-79"
    assert res["level"] == "error"
    assert res["message"]["text"] == "Reflected XSS on /search"
    assert res["properties"]["trace_id"] == "CHK-123"
    assert "OWASP" in res["properties"]["compliance"]
    assert "A03:2021-Injection" in res["properties"]["compliance"]["OWASP"]

def test_sarif_exporter_no_cwe():
    finding = Finding(
        title="Custom Finding",
        severity=Severity.MEDIUM,
        description="Some custom issue",
        cwe="",
        remediation="Fix it"
    )
    result = ScanResult(
        target="http://example.com",
        scanner_name="TestScanner",
        findings=[finding],
        status="completed"
    )
    
    exporter = SARIFExporter(result, chk_id="CHK-456")
    sarif = exporter.generate()
    
    run = sarif["runs"][0]
    res = run["results"][0]
    assert res["ruleId"] == "custom-finding"
    assert res["level"] == "warning"

def test_sarif_exporter_rules_metadata():
    finding = Finding(
        title="SQL Injection",
        severity=Severity.CRITICAL,
        description="SQL injection on /login",
        cwe="CWE-89",
        remediation="Use parameterized queries"
    )
    result = ScanResult(
        target="http://example.com",
        scanner_name="TestScanner",
        findings=[finding],
        status="completed"
    )
    
    exporter = SARIFExporter(result)
    sarif = exporter.generate()
    
    driver = sarif["runs"][0]["tool"]["driver"]
    assert len(driver["rules"]) == 1
    rule = driver["rules"][0]
    assert rule["id"] == "CWE-89"
    assert rule["helpUri"] == "https://cwe.mitre.org/data/definitions/89.html"
    assert rule["shortDescription"]["text"] == "SQL Injection"

def test_sarif_exporter_empty_findings():
    result = ScanResult(
        target="http://example.com",
        scanner_name="TestScanner",
        findings=[],
        status="completed"
    )
    
    exporter = SARIFExporter(result)
    sarif = exporter.generate()
    
    assert len(sarif["runs"][0]["results"]) == 0
