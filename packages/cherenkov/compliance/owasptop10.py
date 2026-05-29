"""OWASP Top 10 Compliance Framework plugin for CHERENKOV."""

from __future__ import annotations

from .base import ComplianceControl, ComplianceFramework


class OWASPTop10(ComplianceFramework):
    """OWASP Top 10 Compliance Framework definition."""

    framework_id = "owasp2021"
    framework_name = "OWASP Top 10"
    framework_version = "2021"
    regulator = "OWASP Foundation"

    @property
    def controls(self) -> list[ComplianceControl]:
        """All controls in OWASP Top 10 2021."""
        return [
            ComplianceControl(
                "A01",
                "Broken Access Control",
                "Access",
                "Access control failures",
                ["CWE-284", "CWE-285", "CWE-639", "CWE-22", "CWE-200"],
                5,
            ),
            ComplianceControl(
                "A02",
                "Cryptographic Failures",
                "Crypto",
                "Cryptography issues",
                ["CWE-319", "CWE-311", "CWE-312", "CWE-327", "CWE-523"],
                5,
            ),
            ComplianceControl(
                "A03",
                "Injection",
                "Injection",
                "Injection flaws",
                ["CWE-89", "CWE-79", "CWE-78", "CWE-77"],
                5,
            ),
            ComplianceControl("A04", "Insecure Design", "Design", "Design flaws", ["CWE-693"], 4),
            ComplianceControl(
                "A05",
                "Security Misconfiguration",
                "Config",
                "Misconfiguration",
                ["CWE-16", "CWE-749", "CWE-1021", "CWE-611"],
                4,
            ),
            ComplianceControl(
                "A06", "Vulnerable Components", "Components", "Known vulnerabilities", [], 4
            ),
            ComplianceControl(
                "A07",
                "Identification and Authentication Failures",
                "Auth",
                "Identification and authentication failures",
                ["CWE-306", "CWE-307", "CWE-308", "CWE-384"],
                5,
            ),
            ComplianceControl(
                "A08", "Software Integrity", "Integrity", "CI/CD and software integrity", [], 4
            ),
            ComplianceControl(
                "A09",
                "Logging Failures",
                "Logging",
                "Insufficient logging",
                ["CWE-778"],
                3,
            ),
            ComplianceControl(
                "A10", "SSRF", "Network", "Server-side request forgery", ["CWE-918"], 4
            ),
        ]
