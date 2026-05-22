# Agent Contracts

This document defines the agent contracts, input/output schemas, and LLM routing decisions.

## Security AI Architect
- **Role**: Reasoning and threat modeling.
- **Inputs**: Target information, initial scope.
- **Outputs**: EngagementPlan.
- **LLM Routing**: `deepseek-r1:14b` for deep reasoning.
- **Data Access**: Queries LATTICE for adaptive memory.

## Red Team Agent
- **Role**: Active exploitation and validation.
- **Inputs**: EngagementPlan, findings from scanners.
- **Outputs**: Exploit payloads, TOKAMAK execution results, CVE mappings.

## SecOps Agent
- **Role**: Compliance and reporting.
- **Inputs**: Validated findings, TOKAMAK results.
- **Outputs**: EGY-FIN CSF Audit report, compliance percentage.
