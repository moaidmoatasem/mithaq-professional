from typing import Any, List

from cherenkov.agents.schemas import ComplianceReport, EngagementPlan
from cherenkov.core.base_scanner import Finding


class SecOpsAgent:
    def __init__(self, mapper: Any = None):
        self.mapper = mapper

    def build_evidence(self, findings: List[Finding]) -> dict:
        return {"findings_count": len(findings), "raw_findings": [f.model_dump() for f in findings]}

    def generate_recs(self, mapped: List[Any]) -> List[str]:
        recs = []
        for m in mapped:
            if not m.passed and getattr(m, "recommendation", None):
                recs.append(m.recommendation)
        return recs

    async def execute(self, plan: EngagementPlan, findings: List[Finding]) -> ComplianceReport:
        mapped = []
        if self.mapper:
            mapped = self.mapper.map_to_framework(findings, plan.compliance_framework)

        return ComplianceReport(
            controls_tested=len(mapped),
            controls_passed=len([m for m in mapped if m.passed]),
            evidence_package=self.build_evidence(findings),
            recommendations=self.generate_recs(mapped),
        )
