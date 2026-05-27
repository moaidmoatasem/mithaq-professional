"""SAMA CSF Compliance Framework plugin for CHERENKOV."""

from __future__ import annotations

from .base import ComplianceControl, ComplianceFramework


class SamaCSF(ComplianceFramework):
    """SAMA CSF Compliance Framework definition."""

    framework_id = "samacsf"
    framework_name = "SAMA CSF"
    framework_version = "2.0"
    regulator = "Saudi Central Bank (SAMA)"

    @property
    def controls(self) -> list[ComplianceControl]:
        """All controls in SAMA CSF."""
        return [
            ComplianceControl(
                "3.1", "Cybersecurity Leadership", "Governance", "Leadership commitment", [], 3
            ),
            ComplianceControl(
                "3.2",
                "Cybersecurity Risk Management",
                "Governance",
                "Risk framework",
                ["CWE-693", "CWE-16"],
                4,
            ),
            ComplianceControl(
                "3.3",
                "Cybersecurity in Projects",
                "Governance",
                "Security in SDLC",
                ["CWE-89", "CWE-79", "CWE-434"],
                4,
            ),
            ComplianceControl(
                "3.4", "Third-Party Cybersecurity", "Governance", "Supply chain security", [], 3
            ),
            ComplianceControl(
                "4.1",
                "Identity and Access Management",
                "Protect",
                "IAM controls",
                ["CWE-284", "CWE-285", "CWE-306", "CWE-307"],
                5,
            ),
            ComplianceControl(
                "4.2",
                "Data and Information Protection",
                "Protect",
                "Data protection",
                ["CWE-319", "CWE-311", "CWE-312"],
                5,
            ),
            ComplianceControl(
                "4.3",
                "Secure Configuration",
                "Protect",
                "Hardening",
                ["CWE-749", "CWE-693", "CWE-1021"],
                4,
            ),
            ComplianceControl(
                "4.4",
                "Vulnerability Management",
                "Protect",
                "Vuln scanning and patching",
                ["CWE-89", "CWE-79", "CWE-22", "CWE-611"],
                5,
            ),
            ComplianceControl(
                "4.5",
                "Security Monitoring",
                "Detect",
                "Logging and monitoring",
                ["CWE-778", "CWE-200"],
                4,
            ),
            ComplianceControl(
                "4.6", "Cybersecurity Incident Management", "Respond", "Incident handling", [], 4
            ),
        ]
