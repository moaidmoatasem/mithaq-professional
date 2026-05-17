from __future__ import annotations

import time
from typing import Dict, List, Optional

from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity
from cherenkov.threat_modeling.dfd_generator import DFDGenerator
from cherenkov.threat_modeling.schemas import ThreatModel

STRIDE_TO_CWE: Dict[str, str] = {
    "Spoofing": "CWE-287",
    "Tampering": "CWE-353",
    "Repudiation": "CWE-778",
    "Information Disclosure": "CWE-200",
    "Denial of Service": "CWE-770",
    "Elevation of Privilege": "CWE-269",
}


class ThreatModelScanner(BaseScanner):
    """Performs automated threat modeling by analyzing system descriptions.

    Generates DFDs, identifies threats using STRIDE, and exports to
    industry-standard formats (Threat Dragon v2, TM-BOM, Mermaid).
    Operates as a standard scanner in the scanning pipeline.
    """

    def __init__(self):
        super().__init__(
            name="threat_model",
            description="Automated STRIDE threat modeling with DFD generation and Threat Dragon export",
        )
        self._generator = DFDGenerator()

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        """Generate a threat model from a system description.

        Args:
            target: A URL or system description to analyze.
            timeout: Maximum time for analysis.

        Returns:
            ScanResult with threats identified as findings.
        """
        start = time.monotonic()

        if target.startswith(("http://", "https://")):
            description = f"Web application at {target}"
        else:
            description = target

        model = self._generator.generate(
            system_description=description,
            architecture_pattern="web_app",
        )

        findings: List[Finding] = []
        for diagram in model.diagrams:
            for threat in diagram.threats:
                sev_map = {
                    "CRITICAL": Severity.CRITICAL,
                    "HIGH": Severity.HIGH,
                    "MEDIUM": Severity.MEDIUM,
                    "LOW": Severity.LOW,
                    "INFO": Severity.INFO,
                }
                findings.append(
                    Finding(
                        title=f"[{threat.model_type}] {threat.title}",
                        severity=sev_map.get(threat.severity.value, Severity.MEDIUM),
                        description=f"{threat.description}\n\n"
                        f"**Mitigation**: {threat.mitigation}",
                        cwe=threat.cwe or STRIDE_TO_CWE.get(threat.type, "CWE-0"),
                        remediation=threat.mitigation,
                    )
                )

        duration = (time.monotonic() - start) * 1000

        return ScanResult(
            target=target,
            scanner_name=self.name,
            findings=findings,
            duration_ms=duration,
            status="completed",
        )
