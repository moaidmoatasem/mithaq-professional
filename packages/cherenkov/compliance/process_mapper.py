"""Business Process → Security Controls Mapper"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from cherenkov.compliance.mapper import ComplianceMapper

___FRAMEWORKS = ["OWASP", "SAMA_CSF", "EGY_FIN_CSF", "DORA"]


@dataclass
class ProcessStep:
    step_id: str
    name: str
    description: str
    cwe_ids: list[str] = field(default_factory=list)
    risk_level: str = "medium"


@dataclass
class BusinessProcess:
    process_id: str
    name: str
    description: str
    category: str
    steps: list[ProcessStep] = field(default_factory=list)


PROCESSES: dict[str, BusinessProcess] = {
    "user_authentication": BusinessProcess(
        process_id="user_authentication",
        name="User Authentication",
        description="User login, credential validation, and session management flow",
        category="authentication",
        steps=[
            ProcessStep(
                step_id="auth-1",
                name="Credential Input",
                description="User submits credentials",
                cwe_ids=["CWE-502", "CWE-798", "CWE-312"],
                risk_level="high",
            ),
            ProcessStep(
                step_id="auth-2",
                name="Credential Validation",
                description="Server validates credentials",
                cwe_ids=["CWE-287", "CWE-306", "CWE-89"],
                risk_level="critical",
            ),
            ProcessStep(
                step_id="auth-3",
                name="Session Creation",
                description="Generate session token after auth",
                cwe_ids=["CWE-319", "CWE-601", "CWE-352"],
                risk_level="high",
            ),
            ProcessStep(
                step_id="auth-4",
                name="Session Validation",
                description="Verify session on subsequent requests",
                cwe_ids=["CWE-287", "CWE-601"],
                risk_level="medium",
            ),
        ],
    ),
    "payment_processing": BusinessProcess(
        process_id="payment_processing",
        name="Payment Processing",
        description="End-to-end payment transaction flow",
        category="financial",
        steps=[
            ProcessStep(
                step_id="pay-1",
                name="Payment Initiation",
                description="User enters payment details",
                cwe_ids=["CWE-312", "CWE-319", "CWE-79"],
                risk_level="critical",
            ),
            ProcessStep(
                step_id="pay-2",
                name="Payment Validation",
                description="Validate card and billing",
                cwe_ids=["CWE-20", "CWE-89", "CWE-79"],
                risk_level="high",
            ),
            ProcessStep(
                step_id="pay-3",
                name="Transaction Processing",
                description="Route through payment gateway",
                cwe_ids=["CWE-918", "CWE-319", "CWE-312"],
                risk_level="critical",
            ),
            ProcessStep(
                step_id="pay-4",
                name="Transaction Logging",
                description="Record in audit trail",
                cwe_ids=["CWE-732", "CWE-200", "CWE-312"],
                risk_level="high",
            ),
        ],
    ),
    "file_upload": BusinessProcess(
        process_id="file_upload",
        name="File Upload & Processing",
        description="File upload, validation, storage, and retrieval flow",
        category="data_management",
        steps=[
            ProcessStep(
                step_id="upload-1",
                name="File Reception",
                description="Accept uploaded file",
                cwe_ids=["CWE-434", "CWE-79", "CWE-20"],
                risk_level="critical",
            ),
            ProcessStep(
                step_id="upload-2",
                name="File Validation",
                description="Validate type and size",
                cwe_ids=["CWE-20", "CWE-434", "CWE-502"],
                risk_level="high",
            ),
            ProcessStep(
                step_id="upload-3",
                name="File Storage",
                description="Store in filesystem",
                cwe_ids=["CWE-22", "CWE-732", "CWE-502"],
                risk_level="high",
            ),
            ProcessStep(
                step_id="upload-4",
                name="File Retrieval",
                description="Serve to authorized users",
                cwe_ids=["CWE-22", "CWE-200", "CWE-601"],
                risk_level="medium",
            ),
        ],
    ),
}


RISK_WEIGHTS: dict[str, int] = {"low": 1, "medium": 2, "high": 3, "critical": 4}


class ProcessMapper:
    @staticmethod
    def list_processes(category: Optional[str] = None) -> list[dict[str, str]]:
        processes = []
        for proc in PROCESSES.values():
            if category and proc.category != category:
                continue
            processes.append(
                {
                    "process_id": proc.process_id,
                    "name": proc.name,
                    "description": proc.description,
                    "category": proc.category,
                    "step_count": len(proc.steps),
                }
            )
        return processes

    @staticmethod
    def get_process(process_id: str) -> Optional[dict]:
        proc = PROCESSES.get(process_id)
        if not proc:
            return None
        steps = []
        for step in proc.steps:
            controls = [
                {"cwe_id": cwe_id, "compliance": ComplianceMapper.map_all(cwe_id)}
                for cwe_id in step.cwe_ids
            ]
            steps.append(
                {
                    "step_id": step.step_id,
                    "name": step.name,
                    "description": step.description,
                    "risk_level": step.risk_level,
                    "controls": controls,
                }
            )
        return {
            "process_id": proc.process_id,
            "name": proc.name,
            "description": proc.description,
            "category": proc.category,
            "steps": steps,
        }

    @staticmethod
    def generate_risk_report(process_id: str) -> dict:
        proc = PROCESSES.get(process_id)
        if not proc:
            return {"error": "Process not found"}
        total_steps = len(proc.steps)
        risk_scores: list[int] = [RISK_WEIGHTS.get(step.risk_level, 2) for step in proc.steps]
        cwe_coverage: dict[str, int] = {
            fw: 0 for fw in ["OWASP", "SAMA_CSF", "EGY_FIN_CSF", "DORA"]
        }
        critical_steps: list[str] = []
        high_steps: list[str] = []
        all_cwes: set[str] = set()
        for step in proc.steps:
            for cwe_id in step.cwe_ids:
                all_cwes.add(cwe_id)
                for fw in ["OWASP", "SAMA_CSF", "EGY_FIN_CSF", "DORA"]:
                    if ComplianceMapper.map(cwe_id, fw):
                        cwe_coverage[fw] += 1

        avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0
        max_risk = max(risk_scores) if risk_scores else 0

        compliance_coverage = {}
        for fw in ["OWASP", "SAMA_CSF", "EGY_FIN_CSF", "DORA"]:
            total_possible = total_steps * len(all_cwes)
            coverage_pct = (cwe_coverage[fw] / total_possible * 100) if total_possible > 0 else 0
            compliance_coverage[fw] = {
                "controls_mapped": cwe_coverage[fw],
                "coverage_percentage": round(coverage_pct, 1),
            }

        return {
            "process_id": proc.process_id,
            "process_name": proc.name,
            "category": proc.category,
            "risk_summary": {
                "total_steps": total_steps,
                "average_risk_score": round(avg_risk, 2),
                "max_risk_score": max_risk,
                "critical_steps": critical_steps,
                "high_risk_steps": high_steps,
            },
            "compliance_coverage": compliance_coverage,
            "unique_cwes": sorted(all_cwes),
            "total_unique_cwes": len(all_cwes),
        }

    @staticmethod
    def list_categories() -> list[str]:
        return sorted(set(proc.category for proc in PROCESSES.values()))
