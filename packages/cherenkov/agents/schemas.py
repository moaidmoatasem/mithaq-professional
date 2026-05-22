from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from cherenkov.core.base_scanner import Finding

class EngagementPlan(BaseModel):
    target: str
    red_team_tasks: List[Dict[str, Any]]
    compliance_framework: str

class ComplianceReport(BaseModel):
    controls_tested: int
    controls_passed: int
    evidence_package: dict
    recommendations: List[str]
