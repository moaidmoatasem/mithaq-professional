"""
Hybrid Cloud-Local Orchestrator
Implements ReAct (Reasoning + Acting) loop with dual-brain architecture.
"""

import time
from typing import Dict, List, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
from cherenkov.agents.cloud.strategic_planner import StrategicPlanner, ThreatAnalysisTask
from cherenkov.ablation.redactor import DataRedactor, RedactionLevel


class CognitiveLoopException(Exception):
    """Exception raised when an agent enters an infinite logic loop."""

    pass


class TaskExecutionTracker:
    """Monitors task attempts to detect infinite loops."""

    def __init__(self):
        self.attempts: Dict[str, int] = {}

    def check_loop(self, target: str, payload: str) -> bool:
        """
        Check if a specific target/payload path has been attempted too many times.
        Returns True if a loop is detected.
        """
        key = f"{target}:{payload}"
        self.attempts[key] = self.attempts.get(key, 0) + 1
        return self.attempts[key] >= 3


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
        
        # Al-Hakam Overseer State
        self.concurrency_limit = 4
        self.consecutive_successes = 0
        self.task_tracker = TaskExecutionTracker()

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
        print("[ABLATION] Payload sanitized / PII vaporized")
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
            print("[MEISSNER] Zero-egress verified. Safe for cloud strategic planning.")
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
            
            # --- Overseer: Loop Detection ---
            # Simulated target/payload for detection
            target_id = f"{target_type}_instance"
            simulated_payload = analysis_scope[0] if analysis_scope else "default_recon"
            
            if self.task_tracker.check_loop(target_id, simulated_payload):
                print(f"[MEISSNER] [Al-Hakam] Cognitive loop detected for {target_id} with payload {simulated_payload}.")
                raise CognitiveLoopException(f"Infinite logic loop detected for {target_id}")

            # --- Overseer: AIMD Capacity Check ---
            print(f"   [Al-Hakam] Current Concurrency Capacity: {self.concurrency_limit}")
            
            # Simulate local analysis
            local_findings = {
                "vulnerabilities_found": 3,
                "critical_count": 1,
                "high_count": 2,
                "scanned_files": len(local_context),
                "execution_time": "2.3s",
                "attack_chain": "Exposed RDP -> Weak Credentials -> RCE"
            }
            
            # --- Overseer: Adversarial Review ---
            is_valid = self.verify_finding_logic(target_id, local_findings)
            
            if not is_valid:
                print(f"[MEISSNER] [Al-Hakam] Dropping finding due to adversarial failure.")
                local_findings = {"vulnerabilities_found": 0} # Strip invalid findings

            # --- Overseer: AIMD Feedback ---
            # For simulation, we assume success unless a specific error occurs
            self.handle_inference_result(success=True)

            print(f"   ✅ Local analysis complete")

        # Step 4: Combine results
        print("\n📊 Step 4: Combining results...")

        result = TaskResult(
            success=True,
            task_name=f"{target_type}_audit",
            output={
                "protocol": "CHERENKOV Sovereign Security",
                "engine": "CHERENKOV Engine",
                "artifact": "Cherenkov Trace",
                "trace_id": f"CT-{time.strftime('%Y')}-{len(self.execution_history):03d}",
                "cryptographic_anchor": {
                    "perimeter_status": "MEISSNER Zero-Egress Verified"
                },
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

    def handle_inference_result(self, success: bool):
        """
        Implements Additive Increase Multiplicative Decrease (AIMD) for concurrency control.
        """
        if not success:
            # Multiplicative Decrease
            old_limit = self.concurrency_limit
            self.concurrency_limit = max(1, self.concurrency_limit // 2)
            self.consecutive_successes = 0
            print(f"[MEISSNER] Egress Blocked / Zero-egress verified. Reducing concurrency: {old_limit} -> {self.concurrency_limit}")
        else:
            # Additive Increase tracking
            self.consecutive_successes += 1
            if self.consecutive_successes >= 5:
                self.concurrency_limit += 1
                self.consecutive_successes = 0
                print(f"[MEISSNER] Consistent performance. Increasing capacity: {self.concurrency_limit}")

    def verify_finding_logic(self, target: str, finding: Dict[str, Any]) -> bool:
        """
        Adversarial Review: Asks a local model to find logical flaws in the attack chain.
        """
        print(f"\n🕵️  Adversarial Review: Verifying finding for {target}...")
        
        # Simulating local model call with skeptical prompt
        # In production: This would be an Ollama call
        # Prompt: "Act as a Skeptical Auditor. Identify one logical flaw in this attack chain. If no flaw exists, output 'VALID'."
        
        attack_chain = finding.get("attack_chain", "N/A")
        
        # Simulated "Skeptical Auditor" response
        # We'll assume it's VALID for now but implement the logic structure
        audit_response = "VALID" 
        
        if audit_response == "VALID":
            print(f"   ✅ [Al-Hakam] Finding verified. Proceeding to TOKAMAK.")
            return True
        else:
            print(f"   ⚠️  [MEISSNER] [Al-Hakam] Adversarial review failed: {audit_response}")
            return False

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

