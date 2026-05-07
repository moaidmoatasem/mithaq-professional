# MITHAQ Integrations & Approvals

## 1. External Integrations (Zero-Egress Compliant)

MITHAQ is designed to be air-gapped. However, optional integrations are supported provided they route through the SIYAADA redaction engine.

### 1.1 Local LLMs (Primary)
*   **Engine:** Ollama
*   **Models:** Qwen2.5 (Coder), Llama 3.2.
*   **Integration Point:** Local REST API (`http://localhost:11434`).
*   **Data Scope:** Full unredacted data access.

### 1.2 Cloud LLMs (Secondary / Fallback)
*   **Providers:** Groq, Gemini, Claude.
*   **Integration Point:** Respective HTTP APIs.
*   **Data Scope:** STRICTLY REDACTED. Data must pass through `SiyaadaSanitizer` before egress.

### 1.3 Security Tools
*   **Mobile:** APKTool, Androguard (Local wrappers).
*   **Dynamic:** Drozer, Frida (Local hooks).

## 2. New Ideas & Feature Approvals

MITHAQ relies heavily on AI agents for development. To maintain control, a strict approval workflow is enforced.

### 2.1 The Approval Workflow

1.  **Idea Generation:** An AI agent proposes a new feature, scanner, or architectural change by creating a Draft Pull Request or Issue with the label `idea-proposal`.
2.  **Architect Review (AI):** The *Al-Muhandis* agent reviews the proposal against the `MITHAQ_SOVEREIGN_BLUEPRINT.md` and `SYSTEM_DESIGN.md`. If it violates core principles (e.g., zero-egress), it is rejected.
3.  **Human-in-the-Loop (HITL) Review:** If the proposal passes AI review, it requires approval from a human Technical Product Manager or Lead Architect.
4.  **Implementation:** Once approved, the issue is labeled `approved-for-dev` and added to the active sprint.

### 2.2 Security Changes (CRITICAL)

Any changes to the following components require a **Mandatory Human Review** regardless of the AI Architect's decision:
*   DAREE3 (Network Proxy rules).
*   SIYAADA (Redaction regex, logic, or HMAC signing).
*   AL-BURHAN (Sandbox configuration or execution rules).
*   Authentication / RBAC logic.

Agents are strictly forbidden from automatically merging PRs that modify these paths.
