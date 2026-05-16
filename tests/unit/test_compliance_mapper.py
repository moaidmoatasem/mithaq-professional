from cherenkov.compliance import ComplianceMapper
from cherenkov.compliance.mapper import FRAMEWORKS


def test_mapper_owasp_cwe79():
    result = ComplianceMapper.map("CWE-79", "OWASP")
    assert isinstance(result, list)
    assert len(result) > 0
    assert "A03:2021-Injection" in result


def test_mapper_egy_fin():
    result = ComplianceMapper.map("CWE-89", "EGY_FIN_CSF")
    assert isinstance(result, list)
    assert len(result) > 0
    assert "CBE-2.1.4" in result


def test_mapper_sama():
    result = ComplianceMapper.map("CWE-22", "SAMA_CSF")
    assert isinstance(result, list)
    assert len(result) > 0
    assert "SAMA-3.2.1" in result


def test_mapper_dora():
    result = ComplianceMapper.map("CWE-918", "DORA")
    assert isinstance(result, list)
    assert len(result) > 0
    assert "ART-9.10" in result


def test_mapper_dora_art_9_4():
    result = ComplianceMapper.map("CWE-352", "DORA")
    assert "ART-9.4" in result


def test_mapper_unknown_cwe_returns_empty():
    assert ComplianceMapper.map("CWE-9999", "OWASP") == []
    assert ComplianceMapper.map("CWE-9999", "SAMA_CSF") == []
    assert ComplianceMapper.map("CWE-9999", "EGY_FIN_CSF") == []
    assert ComplianceMapper.map("CWE-9999", "DORA") == []


def test_mapper_unknown_framework_returns_empty():
    assert ComplianceMapper.map("CWE-79", "UNKNOWN_FRAMEWORK") == []


def test_map_all_returns_all_frameworks():
    result = ComplianceMapper.map_all("CWE-79")
    assert isinstance(result, dict)
    assert "OWASP" in result
    assert "SAMA_CSF" in result
    assert "EGY_FIN_CSF" in result
    assert "DORA" in result


def test_map_all_unknown_returns_empty():
    assert ComplianceMapper.map_all("CWE-9999") == {}


def test_list_cwes():
    cwes = ComplianceMapper.list_cwes()
    assert len(cwes) >= 9
    assert "CWE-79" in cwes
    assert "CWE-918" in cwes


def test_coverage_all_frameworks():
    cov = ComplianceMapper.coverage()
    assert "OWASP" in cov
    assert "SAMA_CSF" in cov
    assert "EGY_FIN_CSF" in cov
    assert "DORA" in cov
    assert cov["OWASP"] == cov["SAMA_CSF"] == cov["EGY_FIN_CSF"] == cov["DORA"]
    assert cov["OWASP"] >= 9


def test_cwe_minimum_coverage():
    assert len(ComplianceMapper.list_cwes()) >= 19


def test_every_cwe_has_all_frameworks():
    for cwe in ComplianceMapper.list_cwes():
        mappings = ComplianceMapper.map_all(cwe)
        for fw in FRAMEWORKS:
            assert fw in mappings, f"{cwe} missing {fw}"
            assert len(mappings[fw]) > 0, f"{cwe} has empty {fw}"


def test_each_framework_has_expected_controls():
    controls = {
        "CWE-79": {"OWASP": "A03:2021-Injection"},
        "CWE-89": {"OWASP": "A03:2021-Injection"},
        "CWE-22": {"OWASP": "A01:2021-Broken Access Control"},
        "CWE-918": {"OWASP": "A10:2021-Server-Side Request Forgery"},
    }
    for cwe, expected in controls.items():
        for fw, val in expected.items():
            assert val in ComplianceMapper.map(cwe, fw)
