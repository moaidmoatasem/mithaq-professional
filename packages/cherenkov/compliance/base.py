"""Base compliance classes and models for the CHERENKOV Compliance Plugin System."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ComplianceControl:
    """Represents a specific cybersecurity compliance control requirement.

    Attributes:
        id: Control ID (e.g. "PR-01", "AC-7").
        name: Name of the control.
        domain: Category or area (e.g. "Protect", "Govern").
        description: Detailed control description.
        cwe_list: CWE IDs mapped to this control.
        severity_weight: Criticality level (1-5).
    """

    id: str  # e.g. "PR-01", "AC-7", "SC-28"
    name: str
    domain: str
    description: str
    cwe_list: list[str]
    severity_weight: int  # 1-5


@dataclass
class MappedFinding:
    """A scan finding mapped to framework compliance controls.

    Attributes:
        finding_title: Title of the finding.
        cwe: CWE ID associated with the finding.
        severity: Severity rating of the finding.
        controls: List of control IDs this finding maps to.
        domain: Area domain of the first matched control.
        remediation: Standard remediation guidance.
        compliant: Whether the finding is compliant.
        arabic_text: Optional localized Arabic text description/mapping.
    """

    finding_title: str
    cwe: str
    severity: str
    controls: list[str]
    domain: str
    remediation: str
    compliant: bool = False
    arabic_text: str = ""


@dataclass
class ComplianceReport:
    """Consolidated compliance report generated for a scan.

    Attributes:
        scan_id: Scan identifier.
        framework_id: ID of the compliance framework.
        framework_name: Human readable name of the framework.
        framework_version: Framework version.
        regulator: Governing regulator of the framework.
        controls_total: Total number of controls in the framework.
        controls_tested: Number of controls tested in this run.
        coverage_pct: Percentage of controls tested.
        findings_mapped: Number of findings successfully mapped to controls.
        findings_unmapped: Number of findings that could not be mapped.
        compliance_score: Calculated compliance score percentage.
        mapped_findings: List of mapped findings.
        summary: Standard executive summary string.
        arabic_summary: Optional localized Arabic summary.
    """

    scan_id: str
    framework_id: str
    framework_name: str
    framework_version: str
    regulator: str
    controls_total: int
    controls_tested: int
    coverage_pct: int
    findings_mapped: int
    findings_unmapped: int
    compliance_score: int
    mapped_findings: list[MappedFinding]
    summary: str
    arabic_summary: str = ""


class ComplianceFramework(ABC):
    """Abstract base class representing a regulatory or security compliance framework."""

    @property
    @abstractmethod
    def framework_id(self) -> str:
        """The framework's unique identifier (e.g. 'egyfincsf')."""
        pass

    @property
    @abstractmethod
    def framework_name(self) -> str:
        """Human readable name: e.g. 'EGY-FIN CSF v1.0'."""
        pass

    @property
    @abstractmethod
    def framework_version(self) -> str:
        """Version of the framework: e.g. '1.0'."""
        pass

    @property
    @abstractmethod
    def regulator(self) -> str:
        """The regulator body: e.g. 'Central Bank of Egypt'."""
        pass

    @property
    @abstractmethod
    def controls(self) -> list[ComplianceControl]:
        """All controls in this framework."""
        pass

    @property
    def cwe_map(self) -> dict[str, list[str]]:
        """Auto-built mapping from CWE ID to list of mapped control IDs."""
        result: dict[str, list[str]] = {}
        for ctrl in self.controls:
            for cwe in ctrl.cwe_list:
                result.setdefault(cwe, []).append(ctrl.id)
        return result

    def map_finding(self, finding: dict) -> MappedFinding:
        """Maps a single security finding dictionary to framework controls.

        Args:
            finding: Standard dictionary representation of a scan finding.

        Returns:
            MappedFinding: The mapped compliance control finding.
        """
        cwe = finding.get("cwe", "")
        control_ids = self.cwe_map.get(cwe, ["UNMAPPED"])
        matched = [c for c in self.controls if c.id in control_ids]
        return MappedFinding(
            finding_title=finding.get("title", ""),
            cwe=cwe,
            severity=finding.get("severity", ""),
            controls=control_ids,
            domain=matched[0].domain if matched else "Unknown",
            remediation=finding.get("remediation", ""),
        )

    def generate_report(self, findings: list[dict], scan_id: str) -> ComplianceReport:
        """Generates a compliance report from scan findings.

        Args:
            findings: List of security finding dictionaries.
            scan_id: Unique trace scan identifier.

        Returns:
            ComplianceReport: The compiled compliance report.
        """
        mapped = [self.map_finding(f) for f in findings]
        unmapped = [m for m in mapped if "UNMAPPED" in m.controls]
        covered: set[str] = set()
        for m in mapped:
            covered.update(m.controls)
        covered.discard("UNMAPPED")
        tested = len(covered)
        total = len(self.controls)
        failed = len([m for m in mapped if not m.compliant])
        score = int(((len(mapped) - failed) / max(len(mapped), 1)) * 100)
        return ComplianceReport(
            scan_id=scan_id,
            framework_id=self.framework_id,
            framework_name=self.framework_name,
            framework_version=self.framework_version,
            regulator=self.regulator,
            controls_total=total,
            controls_tested=tested,
            coverage_pct=int((tested / max(total, 1)) * 100),
            findings_mapped=len(mapped) - len(unmapped),
            findings_unmapped=len(unmapped),
            compliance_score=score,
            mapped_findings=mapped,
            summary=(f"{tested}/{total} {self.framework_name} controls assessed. Score: {score}%"),
        )
