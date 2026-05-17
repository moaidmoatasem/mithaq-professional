from __future__ import annotations

FRAMEWORKS = ["OWASP", "SAMA_CSF", "EGY_FIN_CSF", "DORA"]

MAPPING: dict[str, dict[str, list[str]]] = {
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
    "CWE-77": {
        "OWASP": ["A03:2021-Injection"],
        "SAMA_CSF": ["SAMA-3.1.2"],
        "EGY_FIN_CSF": ["CBE-2.1.6"],
        "DORA": ["ART-9.2"],
    },
    "CWE-78": {
        "OWASP": ["A03:2021-Injection"],
        "SAMA_CSF": ["SAMA-3.1.2"],
        "EGY_FIN_CSF": ["CBE-2.1.6"],
        "DORA": ["ART-9.2"],
    },
    "CWE-94": {
        "OWASP": ["A03:2021-Injection"],
        "SAMA_CSF": ["SAMA-3.1.1"],
        "EGY_FIN_CSF": ["CBE-2.1.4"],
        "DORA": ["ART-9.2"],
    },
    "CWE-306": {
        "OWASP": ["A07:2021-Identification and Authentication Failures"],
        "SAMA_CSF": ["SAMA-3.2.2"],
        "EGY_FIN_CSF": ["CBE-2.2.2"],
        "DORA": ["ART-9.6"],
    },
    "CWE-312": {
        "OWASP": ["A02:2021-Cryptographic Failures"],
        "SAMA_CSF": ["SAMA-4.1.1"],
        "EGY_FIN_CSF": ["CBE-2.8.1"],
        "DORA": ["ART-9.7"],
    },
    "CWE-319": {
        "OWASP": ["A02:2021-Cryptographic Failures"],
        "SAMA_CSF": ["SAMA-4.1.2"],
        "EGY_FIN_CSF": ["CBE-2.8.2"],
        "DORA": ["ART-9.7"],
    },
    "CWE-434": {
        "OWASP": ["A01:2021-Broken Access Control"],
        "SAMA_CSF": ["SAMA-3.2.3"],
        "EGY_FIN_CSF": ["CBE-2.2.3"],
        "DORA": ["ART-9.3"],
    },
    "CWE-601": {
        "OWASP": ["A01:2021-Broken Access Control"],
        "SAMA_CSF": ["SAMA-3.2.4"],
        "EGY_FIN_CSF": ["CBE-2.2.4"],
        "DORA": ["ART-9.4"],
    },
    "CWE-732": {
        "OWASP": ["A01:2021-Broken Access Control"],
        "SAMA_CSF": ["SAMA-3.2.5"],
        "EGY_FIN_CSF": ["CBE-2.2.5"],
        "DORA": ["ART-9.3"],
    },
}


class ComplianceMapper:
    @staticmethod
    def map(cwe: str, framework: str) -> list[str]:
        return MAPPING.get(cwe, {}).get(framework, [])

    @staticmethod
    def map_all(cwe: str) -> dict[str, list[str]]:
        return MAPPING.get(cwe, {})

    @staticmethod
    def list_cwes() -> list[str]:
        return sorted(MAPPING.keys())

    @staticmethod
    def coverage() -> dict[str, int]:
        return {fw: sum(1 for c in MAPPING if fw in MAPPING[c]) for fw in FRAMEWORKS}
