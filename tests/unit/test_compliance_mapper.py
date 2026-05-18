from cherenkov.compliance import ComplianceMapper


def test_cwe79_mapping():
    tags = ComplianceMapper.map_all("CWE-79")
    assert "OWASP" in tags
    assert "A03:2021-Injection" in tags["OWASP"]
    assert "SAMA_CSF" in tags
    assert "SAMA-3.1.1" in tags["SAMA_CSF"]


def test_specific_framework_mapping():
    owasp_tags = ComplianceMapper.map("CWE-89", "OWASP")
    assert owasp_tags == ["A03:2021-Injection"]


def test_unknown_cwe_returns_empty():
    assert ComplianceMapper.map_all("CWE-999") == {}
    assert ComplianceMapper.map("CWE-999", "OWASP") == []


def test_unknown_framework_returns_empty():
    assert ComplianceMapper.map("CWE-79", "UNKNOWN") == []
