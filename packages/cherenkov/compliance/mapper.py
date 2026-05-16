"""Compliance Mapper for CWE to regulatory frameworks."""

MAPPING = {
    "CWE-79": {
        "OWASP": ["A03:2021-Injection"],
        "SAMA_CSF": ["SAMA-3.1.1", "SAMA-3.1.2"],
        "EGY_FIN_CSF": ["CBE-2.1.4"],
        "DORA": ["ART-9.2"],
    },
    "CWE-89": {
        "OWASP": ["A03:2021-Injection"],
        "SAMA_CSF": ["SAMA-3.1.1"],
        "EGY_FIN_CSF": ["CBE-2.1.4"],
        "DORA": ["ART-9.2"],
    },
    "CWE-22": {
        "OWASP": ["A01:2021-Broken Access Control"],
        "SAMA_CSF": ["SAMA-3.2.1"],
        "EGY_FIN_CSF": ["CBE-2.2.1"],
        "DORA": ["ART-9.3"],
    },
    "CWE-352": {
        "OWASP": ["A01:2021-Broken Access Control"],
        "SAMA_CSF": ["SAMA-3.1.3"],
        "EGY_FIN_CSF": ["CBE-2.1.5"],
        "DORA": ["ART-9.4"],
    },
    "CWE-611": {
        "OWASP": ["A05:2021-Security Misconfiguration"],
        "SAMA_CSF": ["SAMA-3.3.1"],
        "EGY_FIN_CSF": ["CBE-2.3.1"],
        "DORA": ["ART-9.5"],
    },
    "CWE-287": {
        "OWASP": ["A07:2021-Identification and Authentication Failures"],
        "SAMA_CSF": ["SAMA-3.4.1"],
        "EGY_FIN_CSF": ["CBE-2.4.1"],
        "DORA": ["ART-9.6"],
    },
    "CWE-798": {
        "OWASP": ["A07:2021-Identification and Authentication Failures"],
        "SAMA_CSF": ["SAMA-3.4.2"],
        "EGY_FIN_CSF": ["CBE-2.4.2"],
        "DORA": ["ART-9.7"],
    },
    "CWE-502": {
        "OWASP": ["A08:2021-Software and Data Integrity Failures"],
        "SAMA_CSF": ["SAMA-3.5.1"],
        "EGY_FIN_CSF": ["CBE-2.5.1"],
        "DORA": ["ART-9.8"],
    },
    "CWE-200": {
        "OWASP": ["A01:2021-Broken Access Control"],
        "SAMA_CSF": ["SAMA-3.6.1"],
        "EGY_FIN_CSF": ["CBE-2.6.1"],
        "DORA": ["ART-9.9"],
    },
    "CWE-918": {
        "OWASP": ["A10:2021-Server-Side Request Forgery"],
        "SAMA_CSF": ["SAMA-3.7.1"],
        "EGY_FIN_CSF": ["CBE-2.7.1"],
        "DORA": ["ART-9.10"],
    },
}


class ComplianceMapper:
    @staticmethod
    def map(cwe: str, framework: str) -> list[str]:
        """Map a CWE to a specific framework's control IDs."""
        return MAPPING.get(cwe, {}).get(framework, [])
