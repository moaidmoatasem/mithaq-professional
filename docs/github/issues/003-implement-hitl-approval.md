---
name: "TASK: Implement HITL Cryptographic Approval"
about: "Require human cryptographic approval for critical workflow execution."
title: "[SECURITY] Implement Human-in-the-Loop (HITL) for TOKAMAK Sandboxing"
labels: ["security", "sprint-4", "human-review-required"]
assignees: "AI-Agent-Architect"
---

## Description
To ensure sovereign safety, AI agents cannot autonomously execute CRITICAL or HIGH severity PoCs in the TOKAMAK sandbox without explicit human consent.

## Tasks
- [ ] Implement an API endpoint `/api/v1/orchestrator/pause` that halts the active mission.
- [ ] Implement an approval schema requiring a cryptographically signed payload from an authorized human user.
- [ ] Ensure the workflow resumes only upon successful validation of the signature.

## Constraints & Review
- **MANDATORY HUMAN REVIEW:** This issue touches core security logic. An AI agent may write the initial code, but a human MUST review the PR, test the cryptographic validation locally, and merge it manually.
- **Fail-Closed:** If the signature is invalid or times out, the workflow MUST terminate and delete the pending PoC payload.
