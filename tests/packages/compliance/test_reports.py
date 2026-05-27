
import pytest
from cherenkov.compliance.reports import PDFReportGenerator, SARIFExporter
from cherenkov.core.base_scanner import ScanResult, Finding, Severity

@pytest.fixture
def sample_result():
    finding = Finding(
        title="SQL Injection",
        severity=Severity.CRITICAL,
        description="A potential SQL injection was found.",
        cwe="CWE-89",
        remediation="Use parameterized queries."
    )
    return ScanResult(
        target="http://localhost",
        scanner_name="TestScanner",
        findings=[finding],
        status="completed"
    )

def test_pdf_report_generation(sample_result):
    compliance_data = {"CWE-89": ["OWASP Top 10", "CWE"]}
    generator = PDFReportGenerator(sample_result, compliance_data, chk_id="CHK-001")
    pdf_output = generator.generate()
    
    # fpdf2 returns a bytearray by default
    pdf_bytes = bytes(pdf_output)
    
    assert len(pdf_bytes) > 0
    # PDF magic number
    assert pdf_bytes.startswith(b"%PDF")

def test_sarif_report_generation(sample_result):
    exporter = SARIFExporter(sample_result, chk_id="CHK-001")
    sarif = exporter.generate()
    
    assert isinstance(sarif, dict)
    assert sarif["version"] == "2.1.0"
    assert len(sarif["runs"]) == 1
    assert len(sarif["runs"][0]["results"]) == 1
    assert sarif["runs"][0]["results"][0]["ruleId"] == "CWE-89"
