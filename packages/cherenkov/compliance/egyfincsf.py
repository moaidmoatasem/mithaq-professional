"""EGY-FIN CSF Compliance Framework plugin for CHERENKOV."""

from __future__ import annotations

from .base import ComplianceControl, ComplianceFramework


class EgyFinCSF(ComplianceFramework):
    """EGY-FIN CSF Compliance Framework definition."""

    framework_id = "egyfincsf"
    framework_name = "EGY-FIN CSF"
    framework_version = "1.0"
    regulator = "Central Bank of Egypt (CBE)"

    @property
    def controls(self) -> list[ComplianceControl]:
        """All controls in EGY-FIN CSF."""
        return [
            ComplianceControl(
                "GV-01",
                "Cybersecurity Governance",
                "Govern",
                "Establish cybersecurity policies",
                [],
                3,
            ),
            ComplianceControl(
                "ID-01",
                "Asset Management",
                "Identify",
                "Inventory assets",
                ["CWE-200", "CWE-1021"],
                3,
            ),
            ComplianceControl(
                "ID-02", "Risk Assessment", "Identify", "Assess risks", ["CWE-693", "CWE-16"], 4
            ),
            ComplianceControl(
                "PR-01",
                "Access Control",
                "Protect",
                "Manage access",
                ["CWE-284", "CWE-285", "CWE-306", "CWE-307", "CWE-308"],
                5,
            ),
            ComplianceControl(
                "PR-02",
                "Data Security",
                "Protect",
                "Protect data at rest and transit",
                ["CWE-319", "CWE-311", "CWE-312", "CWE-327", "CWE-523"],
                5,
            ),
            ComplianceControl(
                "PR-03",
                "Secure Configuration",
                "Protect",
                "Maintain secure configurations",
                ["CWE-16", "CWE-693", "CWE-749", "CWE-1021"],
                4,
            ),
            ComplianceControl(
                "PR-04",
                "Vulnerability Management",
                "Protect",
                "Identify and remediate vulnerabilities",
                ["CWE-89", "CWE-79", "CWE-78", "CWE-22", "CWE-434", "CWE-611"],
                5,
            ),
            ComplianceControl(
                "DE-01",
                "Continuous Monitoring",
                "Detect",
                "Monitor for events",
                ["CWE-778", "CWE-200", "CWE-1021"],
                4,
            ),
            ComplianceControl(
                "RS-01", "Incident Response", "Respond", "Respond to incidents", [], 4
            ),
            ComplianceControl("RC-01", "Recovery", "Recover", "Restore operations", [], 3),
        ]
