# CHERENKOV Design Patterns & Best Practices

To maintain code quality, security, and scalability, all contributions to CHERENKOV must adhere to the following design patterns and best practices.

## 1. Architectural Patterns

### 1.1 AgentGovernor
*   **Description:** A central authority that routes requests to specific agents based on their capabilities and current cognitive load.
*   **Why:** Prevents context window pollution (e.g., sending raw code to a strategist agent) and prevents cascading failures if one agent goes down.

### 1.2 AIMD Circuit Breaker
*   **Description:** Additive Increase, Multiplicative Decrease. When an agent API fails, halve the allowed request rate immediately. When requests succeed, slowly increase the allowed rate linearly.
*   **Why:** Local LLM inference (e.g., Ollama) can easily be overwhelmed. This ensures stability under load.

### 1.3 Proxy Pattern (MEISSNER)
*   **Description:** All outbound network traffic must flow through a proxy that validates the destination against a strict whitelist.
*   **Why:** Enforces zero-egress for sensitive data.

### 1.4 Command Pattern (TOKAMAK)
*   **Description:** Security payloads (PoCs) are encapsulated as command objects before being sent to the sandbox.
*   **Why:** Allows for uniform execution, logging, and cryptographic signing of evidence.

## 2. Frontend UI/UX (Atomic Design)
The UI must be built using Atomic Design principles to ensure reusability and a cohesive look and feel.
*   **Atoms:** Base components (`CyberButton`, `CyberBadge`).
*   **Molecules:** Groups of atoms (`StatCard`, `VulnCard`).
*   **Organisms:** Complex UI sections (`OperationsControl`, `ThreatIntelPanel`).
*   **Templates:** Page layouts (`MainLayout`).

## 3. Best Practices

### 3.1 Security First
*   **Never Hardcode Secrets:** Use environment variables (`.env`).
*   **Validate Everything:** Use Pydantic schemas for all inputs and outputs between agents and APIs.
*   **Fail Closed:** If a system is unsure about a state (e.g., whether to allow network traffic), the default action must be to block/deny.

### 3.2 Testing
*   **TDD is Mandatory:** Write tests before writing implementation.
*   **Coverage:** Minimum 80% test coverage is enforced.
*   **No External Dependencies in Tests:** Use mocking for any API calls to ensure tests can run air-gapped.

### 3.3 Code Style
*   **Formatters:** Ruff and Black must be used.
*   **Typing:** Strict type hints (`mypy`) are required for all new code.
*   **Docstrings:** Google Python Style Guide must be used for all classes and public functions.
