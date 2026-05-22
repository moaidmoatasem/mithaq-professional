from typing import List, Any
from cherenkov.core.base_scanner import Finding
from cherenkov.agents.schemas import EngagementPlan

class RedTeamAgent:
    def __init__(self, tokamak: Any = None, scanners: dict = None):
        self.tokamak = tokamak
        self.scanners = scanners or {}

    def resolve_scanner(self, vector: str):
        if vector in self.scanners:
            return self.scanners[vector]
        raise ValueError(f"No scanner registered for vector: {vector}")

    async def execute(self, plan: EngagementPlan) -> List[Finding]:
        findings = []
        for task in plan.red_team_tasks:
            scanner = self.resolve_scanner(task["vector"])
            result = await scanner.scan(plan.target)
            for f in result.findings:
                if f.severity in ["HIGH", "CRITICAL"]:
                    f = await self.tokamak.confirm(f)
            findings.extend(result.findings)
        return findings
