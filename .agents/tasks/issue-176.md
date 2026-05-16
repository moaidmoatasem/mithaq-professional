# Task: Issue #176 — Compliance Mapper + SARIF Export

**Branch:** `feat/176-compliance-mapper`
**Labels:** `feature, phase-3, area:compliance, priority:medium`
**PR must contain:** `Closes #176`

## Context files

```
packages/cherenkov/core/base_scanner.py   ← Finding.cwe field
packages/cherenkov/api/main.py            ← add SARIF endpoint
packages/cherenkov/core/storage/database.py ← load scan by ID
```

## Create `packages/cherenkov/compliance/`

### `__init__.py`
```python
from .mapper import ComplianceMapper
__all__ = ["ComplianceMapper"]
```

### `mapper.py` — static local lookup, zero network calls

```python
MAPPING: dict[str, dict[str, list[str]]] = {
    "CWE-79":  {"OWASP": ["A03:2021"], "SAMA_CSF": ["3.3.5"], "EGY_FIN_CSF": ["PR.AC-4"], "DORA": ["Art.9.4"]},
    "CWE-89":  {"OWASP": ["A03:2021"], "SAMA_CSF": ["3.3.6"], "EGY_FIN_CSF": ["PR.DS-5"], "DORA": ["Art.9.4"]},
    "CWE-22":  {"OWASP": ["A01:2021"], "SAMA_CSF": ["3.2.1"], "EGY_FIN_CSF": ["PR.AC-1"], "DORA": ["Art.9.2"]},
    "CWE-352": {"OWASP": ["A01:2021"], "SAMA_CSF": ["3.3.4"], "EGY_FIN_CSF": ["PR.AC-3"], "DORA": ["Art.9.4"]},
    "CWE-611": {"OWASP": ["A05:2021"], "SAMA_CSF": ["3.3.7"], "EGY_FIN_CSF": ["PR.DS-2"], "DORA": ["Art.9.3"]},
    "CWE-287": {"OWASP": ["A07:2021"], "SAMA_CSF": ["3.2.3"], "EGY_FIN_CSF": ["PR.AC-7"], "DORA": ["Art.9.4"]},
    "CWE-798": {"OWASP": ["A07:2021"], "SAMA_CSF": ["3.2.4"], "EGY_FIN_CSF": ["PR.AC-1"], "DORA": ["Art.9.2"]},
    "CWE-502": {"OWASP": ["A08:2021"], "SAMA_CSF": ["3.3.8"], "EGY_FIN_CSF": ["PR.DS-6"], "DORA": ["Art.9.4"]},
    "CWE-200": {"OWASP": ["A01:2021"], "SAMA_CSF": ["3.4.1"], "EGY_FIN_CSF": ["PR.DS-1"], "DORA": ["Art.9.2"]},
    "CWE-918": {"OWASP": ["A10:2021"], "SAMA_CSF": ["3.3.9"], "EGY_FIN_CSF": ["PR.AC-5"], "DORA": ["Art.9.3"]},
    # add more as needed
}

class ComplianceMapper:
    def map(self, cwe: str, framework: str) -> list[str]:
        return MAPPING.get(cwe, {}).get(framework, [])

    def map_all(self, cwe: str) -> dict[str, list[str]]:
        return MAPPING.get(cwe, {})
```

## Add to `packages/cherenkov/api/main.py`

```python
@v1.get("/reports/{scan_id}/sarif")
async def v1_sarif(scan_id: str) -> dict:
    """Emit SARIF 2.1.0 JSON for a completed scan."""
    # Load scan from SQLite, map each finding through ComplianceMapper
    # Return SARIF 2.1.0 structure (schema at https://schemastore.org/schemas/json/sarif-2.1.0.json)
```

## Test

```python
# tests/unit/test_compliance_mapper.py
from cherenkov.compliance import ComplianceMapper

def test_cwe79_owasp():
    m = ComplianceMapper()
    assert "A03:2021" in m.map("CWE-79", "OWASP")

def test_unknown_cwe_returns_empty():
    assert m.map("CWE-9999", "OWASP") == []
```

## Verify

```bash
ruff format packages/ && ruff check packages/ --ignore W,S,B
pytest tests/unit/test_compliance_mapper.py -v
```
