"""DORA Compliance Framework plugin for CHERENKOV."""

from __future__ import annotations

from .base import ComplianceControl, ComplianceFramework


class DORA(ComplianceFramework):
    """DORA (Digital Operational Resilience Act) Compliance Framework definition."""

    framework_id = "dora"
    framework_name = "DORA"
    framework_version = "1.0"
    regulator = "European Union"

    @property
    def controls(self) -> list[ComplianceControl]:
        """All controls in DORA."""
        return [
            ComplianceControl(
                "ART-9.2",
                "Protection and Prevention",
                "Protection",
                "Implement policies and protocols for strong authentication mechanisms and protection of cryptographic keys and data.",
                ["CWE-79", "CWE-89", "CWE-77", "CWE-78", "CWE-94"],
                5,
            ),
            ComplianceControl(
                "ART-9.3",
                "Protection and Prevention - Access Control",
                "Protection",
                "Implement sound physical and logical access controls.",
                ["CWE-22", "CWE-434", "CWE-732"],
                5,
            ),
            ComplianceControl(
                "ART-9.4",
                "Protection and Prevention - Authorization",
                "Protection",
                "Prevent unauthorized access and ensure robust authorization.",
                ["CWE-352", "CWE-601"],
                4,
            ),
            ComplianceControl(
                "ART-9.5",
                "Protection and Prevention - Config",
                "Protection",
                "Maintain secure baseline configurations.",
                ["CWE-611"],
                4,
            ),
            ComplianceControl(
                "ART-9.6",
                "Protection and Prevention - Identity",
                "Protection",
                "Secure identity and access management.",
                ["CWE-287", "CWE-306"],
                5,
            ),
            ComplianceControl(
                "ART-9.7",
                "Protection and Prevention - Cryptography",
                "Protection",
                "Use state-of-the-art cryptographic techniques to protect data.",
                ["CWE-798", "CWE-312", "CWE-319"],
                5,
            ),
            ComplianceControl(
                "ART-9.8",
                "Protection and Prevention - Integrity",
                "Protection",
                "Ensure software and data integrity.",
                ["CWE-502"],
                4,
            ),
            ComplianceControl(
                "ART-9.9",
                "Protection and Prevention - Data Leakage",
                "Protection",
                "Prevent data leakage and information exposure.",
                ["CWE-200"],
                4,
            ),
            ComplianceControl(
                "ART-9.10",
                "Protection and Prevention - Network Security",
                "Protection",
                "Implement robust network security controls.",
                ["CWE-918"],
                4,
            ),
        ]
