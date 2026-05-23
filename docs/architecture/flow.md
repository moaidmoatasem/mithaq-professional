# CHERENKOV Architecture Flow

This document details the request flow and data sovereignty checkpoints.

## Request Flow
1. **Request**: Operator initiates a scan or assessment.
2. **Architect**: Security AI Architect generates an EngagementPlan based on the target and LATTICE queries.
3. **Agents**:
   - Red Team Agent executes the plan and validates findings via TOKAMAK.
   - SecOps Agent processes findings for compliance mapping.
4. **Engine**: Core scanners run in the background (TENSOR/KINETIC engine).
5. **Report**: SecOps Agent produces the final EGY-FIN CSF signed PDF report.

## Data Sovereignty Checkpoints
- **ABLATION Trigger Points**: All outgoing data requests to external APIs/LLMs MUST pass through ABLATION to strip PII, credentials, and code.
- **TOKAMAK Proof**: No HIGH/CRITICAL finding is reported without local validation proof in TOKAMAK.
