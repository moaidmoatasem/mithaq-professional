from cherenkov.compliance.egyfincsf import EgyFinCsfMapper


def test_get_controls_valid_cwe():
    controls = EgyFinCsfMapper.get_controls("CWE-79")
    assert controls == ["CBE-2.1.4"]


def test_get_controls_invalid_cwe():
    controls = EgyFinCsfMapper.get_controls("CWE-UNKNOWN")
    assert controls == []


def test_list_all_mappings():
    mappings = EgyFinCsfMapper.list_all_mappings()
    assert isinstance(mappings, dict)
    assert "CWE-79" in mappings
    assert mappings["CWE-79"] == ["CBE-2.1.4"]
    assert "CWE-89" in mappings
    assert mappings["CWE-89"] == ["CBE-2.1.4"]
    assert "CWE-22" in mappings
    assert mappings["CWE-22"] == ["CBE-2.2.1"]
