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
}

class ComplianceMapper:
    def map(self, cwe: str, framework: str) -> list[str]:
        return MAPPING.get(cwe, {}).get(framework, [])

    def map_all(self, cwe: str) -> dict[str, list[str]]:
        return MAPPING.get(cwe, {})
