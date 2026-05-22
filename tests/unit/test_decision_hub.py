from pathlib import Path

import pytest
from cherenkov.agents.decision_hub import DecisionHub
from cherenkov.core.reasoning_store import ReasoningStore


def test_decision_hub_complete_lifecycle(tmp_path: Path):
    db_path = tmp_path / "decision_traces.db"

    # Initialize the collaborative agent decision hub
    hub = DecisionHub(session_id="sprint-test-session", db_path=db_path)

    # 1. Negotiate & Market Research
    research = hub.negotiate_and_market_research("MiddleEastFinTech", ["MEISSNER Isolation"])
    assert research["market"] == "MiddleEastFinTech"
    assert "SAMA CSF" in research["regulatory_compliance_required"]
    assert "Local-first zero-egress sandboxing" in research["competitive_moat"]

    # 2. Scope Definition
    scope = hub.define_scope(
        ["Include dynamic Docker sandbox validations", "Expose HITL approval endpoints"]
    )
    assert (
        "Sprint B: TOKAMAK Pydantic V2 Docker sandbox wrapper implementation"
        in scope["scoped_tasks"]
    )
    assert "Sprint C: Expose /api/v1/hitl approvals operator endpoint" in scope["scoped_tasks"]
    assert "Zero-egress MEISSNER shield" in scope["invariants_enforced"]

    # 3. Milestone Planning
    plan = hub.plan(scope)
    assert plan["sprint_name"] == "Sprint B & C Integration"
    assert "ruff format packages/ tests/" in plan["checklists"]["python_precommit"]

    # 4. System Design
    design = hub.design(
        "Mobile Scanner Gateway", ["Unsanitized IPC bindings", "Egress bypass attempt"]
    )
    assert design["architectural_style"] == "Micro-services with zero-trust IPC bus"
    assert (
        "Non-networked Docker container (--network none)"
        in design["sandbox_capabilities"]["isolation"]
    )

    # 5. Peer Code Review
    review = hub.review("def run_poc(payload): pass", "python")
    assert review["review_status"] == "PASSED_WITH_CONDITIONS"
    assert len(review["identified_risks"]) > 0

    # 6. Redesign Iteration
    redesign = hub.redesign(review)
    assert redesign["iteration_number"] == 1
    assert (
        "Apply dynamic httpx.AsyncClient patching to preserve exception types."
        in redesign["remediations_applied"]
    )

    # 7. Final Governance Approval
    approval = hub.approve({"tests_passing": True, "build_stable": True})
    assert approval["approval_status"] == "AUTHENTICATED"
    assert approval["approver_role"] == "ChiefInformationSecurityOfficer"
    assert len(approval["trace_hash"]) == 64  # SHA256 length

    # 8. Verify ReasoningStore Persistence & Integrity
    store = ReasoningStore(db_path)
    traces = store.query()

    # We performed 7 decision steps, each must carry its own recorded trace
    assert len(traces) == 7
    stages = [t.agent_role for t in traces]

    assert "NEGOTIATION_MARKET_RESEARCH" in stages
    assert "SCOPE_DEFINITION" in stages
    assert "MILESTONE_PLANNING" in stages
    assert "SYSTEM_DESIGN" in stages
    assert "PEER_REVIEW" in stages
    assert "RE-DESIGN_ITERATION" in stages
    assert "FINAL_GOVERNANCE_APPROVAL" in stages

    # Ensure all anchors compute correctly (verifies tamper checks)
    for trace in traces:
        assert trace.sha256_anchor == trace.compute_hash()
