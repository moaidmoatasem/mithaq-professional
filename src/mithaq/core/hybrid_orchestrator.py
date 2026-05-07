"""
Hybrid Cloud-Local Orchestrator
Implements ReAct (Reasoning + Acting) loop with dual-brain architecture.
"""

from typing import Dict, List, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
from mithaq.agents.cloud.strategic_planner import StrategicPlanner, ThreatAnalysisTask
from mithaq.siyaada.redactor import DataRedactor, RedactionLevel


class ExecutionMode(Enum):
    """Execution modes for tasks"""

    CLOUD_ONLY = "cloud_only"  # Strategic planning only
    LOCAL_ONLY = "local_only"  # Sensitive operations only
    HYBRID = "hybrid"  # Default: cloud plans, local executes


class TaskResult(BaseModel):
    """Result of task execution"""

    success: bool
    task_name: str
    output: Dict[str, Any]
    execution_mode: str
    tokens_used: int = 0
    redacted_fields: List[str] = Field(default_factory=list)


class HybridOrchestrator:
    """
    Orchestrates security audits using dual-brain architecture.
    Cloud: Strategic planning (Groq)
    Local: Privileged operations (Ollama)
    """

    def __init__(self, groq_api_key: Optional[str] = None):
        self.cloud_planner = StrategicPlanner(api_key=groq_api_key)
        self.redactor = DataRedactor(level=RedactionLevel.MODERATE)
        self.execution_history: List[TaskResult] = []

    def execute_security_audit(
        self,
        target_type: str,
        local_context: Dict[str, Any],
        analysis_scope: List[str],
        mode: ExecutionMode = ExecutionMode.HYBRID,
    ) -> Dict[str, Any]:
        """
        Execute security audit using hybrid approach.

        Args:
            target_type: Type of target (web, mobile, infra)
            local_context: Sensitive local data (never sent to cloud)
            analysis_scope: Types of analysis to perform
            mode: Execution mode

        Returns:
            Audit results with findings
        """

        print(f"\n🚀 Starting Hybrid Security Audit")
        print(f"   Target: {target_type}")
        print(f"   Mode: {mode.value}")
        print(f"   Scope: {', '.join(analysis_scope)}\n")

        # Step 1: Sanitize local context for cloud
        print("🔒 Step 1: Sanitizing data for cloud transmission...")
        redaction_result = self.redactor.redact_dict(local_context)

        if not redaction_result.is_safe:
            print("   ⚠️  FAIL-CLOSED: Data not safe for cloud. Using local-only mode.")
            mode = ExecutionMode.LOCAL_ONLY
        else:
            print(
                f"   ✅ Redacted {len(redaction_result.redacted_fields)} sensitive fields"
            )

        # Step 2: Cloud strategic planning (if hybrid/cloud mode)
        strategic_plan = None
        tokens_used = 0

        if mode in [ExecutionMode.CLOUD_ONLY, ExecutionMode.HYBRID]:
            print("\n☁️  Step 2: Requesting strategic plan from cloud...")

            # Create breadcrumb for cloud
            breadcrumb = self.redactor.create_breadcrumb(
                local_context, metadata_only=True
            )

            task = ThreatAnalysisTask(
                target_type=target_type,
                abstract_context=breadcrumb,
                analysis_scope=analysis_scope,
            )

            plan_result = self.cloud_planner.plan_security_audit(task)
            strategic_plan = plan_result["plan"]
            tokens_used = plan_result["tokens_used"]

            print(f"   ✅ Strategic plan received ({tokens_used} tokens)")
            print(f"   📋 Plan preview: {strategic_plan[:150]}...")

        # Step 3: Local execution (if hybrid/local mode)
        local_findings = {}

        if mode in [ExecutionMode.LOCAL_ONLY, ExecutionMode.HYBRID]:
            print("\n🔧 Step 3: Executing privileged local analysis...")
            print("   (In production: This would call local Ollama agents)")
            print("   (For now: Simulating local analysis)")

            # Simulate local findings
            local_findings = {
                "vulnerabilities_found": 3,
                "critical_count": 1,
                "high_count": 2,
                "scanned_files": len(local_context),
                "execution_time": "2.3s",
            }

            print(f"   ✅ Local analysis complete")

        # Step 4: Combine results
        print("\n📊 Step 4: Combining results...")

        result = TaskResult(
            success=True,
            task_name=f"{target_type}_audit",
            output={
                "strategic_plan": (
                    strategic_plan if strategic_plan else "Local-only mode"
                ),
                "local_findings": local_findings,
                "redaction_summary": {
                    "redacted_fields": redaction_result.redacted_fields,
                    "hash_signature": redaction_result.hash_signature,
                    "is_safe": redaction_result.is_safe,
                },
            },
            execution_mode=mode.value,
            tokens_used=tokens_used,
            redacted_fields=redaction_result.redacted_fields,
        )

        self.execution_history.append(result)

        print(f"\n✅ Audit complete!")
        print(f"   Mode: {mode.value}")
        print(f"   Tokens used: {tokens_used}")
        print(f"   Redacted fields: {len(redaction_result.redacted_fields)}")

        return result.model_dump()

    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of all executions"""
        return {
            "total_audits": len(self.execution_history),
            "total_tokens": sum(r.tokens_used for r in self.execution_history),
            "modes_used": [r.execution_mode for r in self.execution_history],
            "total_redacted_fields": sum(
                len(r.redacted_fields) for r in self.execution_history
            ),
        }

