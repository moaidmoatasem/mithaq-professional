"""Business Process → Security Controls Mapper

Maps business process flows to security controls (CWEs) and compliance frameworks.
Enables process-specific risk assessment and compliance reporting.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from cherenkov.compliance.mapper import FRAMEWORKS, ComplianceMapper


@dataclass
class ProcessStep:
    """A single step in a business process flow."""

    step_id: str
    name: str
    description: str
    cwe_ids: list[str] = field(default_factory=list)
    risk_level: str = "medium"  # low, medium, high, critical


@dataclass
class BusinessProcess:
    """A complete business process with ordered steps."""

    process_id: str
    name: str
    description: str
    category: str  # e.g., "financial", "authentication", "data_management"
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
                description="User submits username/password or MFA token",
                cwe_ids=["CWE-502", "CWE-798", "CWE-312"],
                risk_level="high",
            ),
            ProcessStep(
                step_id="auth-2",
                name="Credential Validation",
                description="Server validates credentials against identity store",
                cwe_ids=["CWE-287", "CWE-306", "CWE-89"],
                risk_level="critical",
            ),
            ProcessStep(
                step_id="auth-3",
                name="Session Creation",
                description="Generate session token or JWT after successful auth",
                cwe_ids=["CWE-319", "CWE-601", "CWE-352"],
                risk_level="high",
            ),
            ProcessStep(
                step_id="auth-4",
                name="Session Validation",
                description="Verify session token on subsequent requests",
                cwe_ids=["CWE-287", "CWE-601"],
                risk_level="medium",
            ),
        ],
    ),
    "payment_processing": BusinessProcess(
        process_id="payment_processing",
        name="Payment Processing",
        description="End-to-end payment transaction flow from initiation to settlement",
        category="financial",
        steps=[
            ProcessStep(
                step_id="pay-1",
                name="Payment Initiation",
                description="User enters payment details (card, bank, wallet)",
                cwe_ids=["CWE-312", "CWE-319", "CWE-79"],
                risk_level="critical",
            ),
            ProcessStep(
                step_id="pay-2",
                name="Payment Validation",
                description="Validate card number, expiry, CVV, and billing address",
                cwe_ids=["CWE-20", "CWE-89", "CWE-79"],
                risk_level="high",
            ),
            ProcessStep(
                step_id="pay-3",
                name="Transaction Processing",
                description="Route payment through gateway and processor",
                cwe_ids=["CWE-918", "CWE-319", "CWE-312"],
                risk_level="critical",
            ),
            ProcessStep(
                step_id="pay-4",
                name="Transaction Logging",
                description="Record transaction in audit trail and ledger",
                cwe_ids=["CWE-732", "CWE-200", "CWE-312"],
                risk_level="high",
            ),
            ProcessStep(
                step_id="pay-5",
                name="Settlement & Reconciliation",
                description="Finalize payment and reconcile with bank statements",
                cwe_ids=["CWE-732", "CWE-502"],
                risk_level="medium",
            ),
        ],
    ),
    "file_upload": BusinessProcess(
        process_id="file_upload",
        name="File Upload & Processing",
        description="User file upload, validation, storage, and retrieval flow",
        category="data_management",
        steps=[
            ProcessStep(
                step_id="upload-1",
                name="File Reception",
                description="Accept uploaded file from user client",
                cwe_ids=["CWE-434", "CWE-79", "CWE-20"],
                risk_level="critical",
            ),
            ProcessStep(
                step_id="upload-2",
                name="File Validation",
                description="Validate file type, size, and content integrity",
                cwe_ids=["CWE-20", "CWE-434", "CWE-502"],
                risk_level="high",
            ),
            ProcessStep(
                step_id="upload-3",
                name="File Storage",
                description="Store file in filesystem or object storage",
                cwe_ids=["CWE-22", "CWE-732", "CWE-502"],
                risk_level="high",
            ),
            ProcessStep(
                step_id="upload-4",
                name="File Retrieval",
                description="Serve stored file to authorized users",
                cwe_ids=["CWE-22", "CWE-200", "CWE-601"],
                risk_level="medium",
            ),
        ],
    ),
    "data_export": BusinessProcess(
        process_id="data_export",
        name="Data Export & Reporting",
        description="Generate and deliver data exports, reports, and backups",
        category="data_management",
        steps=[
            ProcessStep(
                step_id="export-1",
                name="Data Query",
                description="Query database for export data based on filters",
                cwe_ids=["CWE-89", "CWE-200", "CWE-94"],
                risk_level="high",
            ),
            ProcessStep(
                step_id="export-2",
                name="Data Aggregation",
                description="Aggregate and format data for export",
                cwe_ids=["CWE-200", "CWE-312"],
                risk_level="medium",
            ),
            ProcessStep(
                step_id="export-3",
                name="Report Generation",
                description="Generate PDF, CSV, or Excel report",
                cwe_ids=["CWE-94", "CWE-78", "CWE-77"],
                risk_level="high",
            ),
            ProcessStep(
                step_id="export-4",
                name="Data Delivery",
                description="Deliver export via download, email, or API",
                cwe_ids=["CWE-601", "CWE-918", "CWE-312"],
                risk_level="medium",
            ),
        ],
    ),
    "api_integration": BusinessProcess(
        process_id="api_integration",
        name="Third-Party API Integration",
        description="Integration with external services and APIs",
        category="integration",
        steps=[
            ProcessStep(
                step_id="api-1",
                name="API Authentication",
                description="Authenticate with third-party service (OAuth, API key)",
                cwe_ids=["CWE-798", "CWE-312", "CWE-287"],
                risk_level="high",
            ),
            ProcessStep(
                step_id="api-2",
                name="Request Construction",
                description="Build and sign API requests with parameters",
                cwe_ids=["CWE-918", "CWE-79", "CWE-20"],
                risk_level="medium",
            ),
            ProcessStep(
                step_id="api-3",
                name="Response Processing",
                description="Parse and validate third-party API responses",
                cwe_ids=["CWE-502", "CWE-20", "CWE-79"],
                risk_level="high",
            ),
            ProcessStep(
                step_id="api-4",
                name="Error Handling",
                description="Handle API failures, retries, and fallbacks",
                cwe_ids=["CWE-200", "CWE-732"],
                risk_level="low",
            ),
        ],
    ),
    "user_registration": BusinessProcess(
        process_id="user_registration",
        name="User Registration & Onboarding",
        description="New user account creation and identity verification flow",
        category="authentication",
        steps=[
            ProcessStep(
                step_id="reg-1",
                name="Identity Collection",
                description="Collect user identity information (email, name, DOB)",
                cwe_ids=["CWE-312", "CWE-200", "CWE-79"],
                risk_level="high",
            ),
            ProcessStep(
                step_id="reg-2",
                name="Identity Verification",
                description="Verify email/phone via OTP or document upload",
                cwe_ids=["CWE-287", "CWE-352", "CWE-601"],
                risk_level="high",
            ),
            ProcessStep(
                step_id="reg-3",
                name="Account Creation",
                description="Create user record in identity store",
                cwe_ids=["CWE-89", "CWE-798", "CWE-732"],
                risk_level="critical",
            ),
            ProcessStep(
                step_id="reg-4",
                name="Welcome & Provisioning",
                description="Send welcome email and provision default resources",
                cwe_ids=["CWE-918", "CWE-601"],
                risk_level="low",
            ),
        ],
    ),
    "admin_operations": BusinessProcess(
        process_id="admin_operations",
        name="Administrative Operations",
        description="Admin panel operations including user management and system configuration",
        category="administration",
        steps=[
            ProcessStep(
                step_id="admin-1",
                name="Admin Authentication",
                description="Elevated authentication for admin users",
                cwe_ids=["CWE-287", "CWE-798", "CWE-306"],
                risk_level="critical",
            ),
            ProcessStep(
                step_id="admin-2",
                name="Authorization Check",
                description="Verify admin role and permissions for requested action",
                cwe_ids=["CWE-287", "CWE-269"],
                risk_level="critical",
            ),
            ProcessStep(
                step_id="admin-3",
                name="Operation Execution",
                description="Execute admin operation (user management, config changes)",
                cwe_ids=["CWE-79", "CWE-89", "CWE-78", "CWE-77"],
                risk_level="critical",
            ),
            ProcessStep(
                step_id="admin-4",
                name="Audit Logging",
                description="Record admin action in immutable audit log",
                cwe_ids=["CWE-732", "CWE-200"],
                risk_level="medium",
            ),
        ],
    ),
}

RISK_WEIGHTS: dict[str, int] = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}


class ProcessMapper:
    """Maps business processes to security controls and compliance frameworks."""

    @staticmethod
    def list_processes(category: Optional[str] = None) -> list[dict[str, str]]:
        """List all available business processes, optionally filtered by category."""
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
        """Get a business process with its steps and mapped controls."""
        proc = PROCESSES.get(process_id)
        if not proc:
            return None

        steps = []
        for step in proc.steps:
            controls = []
            for cwe_id in step.cwe_ids:
                controls.append(
                    {
                        "cwe_id": cwe_id,
                        "compliance": ComplianceMapper.map_all(cwe_id),
                    }
                )
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
    def get_process_controls(process_id: str, framework: Optional[str] = None) -> dict:
        """Get all security controls for a process, optionally filtered by compliance framework."""
        proc = PROCESSES.get(process_id)
        if not proc:
            return {"error": "Process not found", "controls": []}

        all_cwes: set[str] = set()
        step_controls: list[dict] = []

        for step in proc.steps:
            step_cwes = []
            for cwe_id in step.cwe_ids:
                all_cwes.add(cwe_id)
                if framework:
                    mapped = ComplianceMapper.map(cwe_id, framework)
                else:
                    mapped = ComplianceMapper.map_all(cwe_id)
                step_cwes.append(
                    {
                        "cwe_id": cwe_id,
                        "framework_controls": mapped,
                    }
                )
            step_controls.append(
                {
                    "step_id": step.step_id,
                    "step_name": step.name,
                    "risk_level": step.risk_level,
                    "controls": step_cwes,
                }
            )

        return {
            "process_id": process_id,
            "process_name": proc.name,
            "total_unique_cwes": len(all_cwes),
            "framework_filter": framework or "all",
            "step_controls": step_controls,
        }

    @staticmethod
    def generate_risk_report(process_id: str) -> dict:
        """Generate a comprehensive risk report for a business process."""
        proc = PROCESSES.get(process_id)
        if not proc:
            return {"error": "Process not found"}

        total_steps = len(proc.steps)
        risk_scores: list[int] = []
        cwe_coverage: dict[str, int] = {fw: 0 for fw in FRAMEWORKS}
        critical_steps: list[str] = []
        high_steps: list[str] = []

        all_cwes: set[str] = set()

        for step in proc.steps:
            risk_scores.append(RISK_WEIGHTS.get(step.risk_level, 2))
            if step.risk_level == "critical":
                critical_steps.append(step.name)
            elif step.risk_level == "high":
                high_steps.append(step.name)

            for cwe_id in step.cwe_ids:
                all_cwes.add(cwe_id)
                for fw in FRAMEWORKS:
                    if ComplianceMapper.map(cwe_id, fw):
                        cwe_coverage[fw] += 1

        avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0
        max_risk = max(risk_scores) if risk_scores else 0

        compliance_coverage = {}
        for fw in FRAMEWORKS:
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
        """List all available process categories."""
        return sorted(set(proc.category for proc in PROCESSES.values()))
