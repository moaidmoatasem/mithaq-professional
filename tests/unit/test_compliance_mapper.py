"""Tests for ComplianceMapper."""

from cherenkov.compliance.mapper import ComplianceMapper

def test_mapper_owasp_cwe79():
    result = ComplianceMapper.map("CWE-79", "OWASP")
    assert isinstance(result, list)
    assert len(result) > 0
    assert "A03:2021-Injection" in result

def test_mapper_unknown():
    assert ComplianceMapper.map("CWE-9999", "OWASP") == []
    assert ComplianceMapper.map("CWE-79", "UNKNOWN_FRAMEWORK") == []
