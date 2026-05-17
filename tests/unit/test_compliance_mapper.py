from cherenkov.compliance import ComplianceMapper

def test_cwe79_mapping():
    mapper = ComplianceMapper()
    tags = mapper.map_all("CWE-79")
    assert "OWASP" in tags
    assert "A03:2021" in tags["OWASP"]
    assert "SAMA_CSF" in tags
    assert "3.3.5" in tags["SAMA_CSF"]

def test_specific_framework_mapping():
    mapper = ComplianceMapper()
    owasp_tags = mapper.map("CWE-89", "OWASP")
    assert owasp_tags == ["A03:2021"]

def test_unknown_cwe_returns_empty():
    mapper = ComplianceMapper()
    assert mapper.map_all("CWE-999") == {}
    assert mapper.map("CWE-999", "OWASP") == []

def test_unknown_framework_returns_empty():
    mapper = ComplianceMapper()
    assert mapper.map("CWE-79", "UNKNOWN") == []
