# CHERENKOV Sovereign Cognitive Defense: Technical Specification

**Version:** 1.2
**Classification:** Sovereign Strategic Asset
**Status:** PRODUCTION LOCKED

This document serves as the Single Source of Truth (SSOT) and Master Technical Blueprint for the CHERENKOV framework. It is formatted for ingestion by LLMs and AI context windows.

---

## 1. Executive Summary & Mission
CHERENKOV is an air-gapped, sovereign AI security and quality intelligence platform. Designed explicitly for highly regulated infrastructures (EGY-FIN CSF, SAMA CSF, DORA), it tests traditional software, mobile applications, and embedded AI systems entirely on local hardware.

**Core Philosophy:**
- **Zero-Egress / Air-Gapped:** Proprietary code or PII never leaves the local environment.
- **Fail-Closed:** Defaults to block/deny if state is uncertain.
- **Mathematical Proof:** Replaces traditional vulnerability scanning with **Kinetic Execution**, meaning it only escalates findings if it can non-destructively execute a Proof of Concept (PoC) locally.

---

## 2. Core Architecture: "The Trident of Truth"

The system architecture is hardcoded to enforce three physical constraints, known as the Trident of Truth:

### 2.1 MEISSNER (The Shield)
- **Role:** The fail-closed network perimeter.
- **Implementation:** Proxy layer (Nginx/Docker) that drops all unauthorized outbound network packets. It intercepts requests and blocks any destination not explicitly whitelisted for local telemetry.
- **Pattern:** Proxy Pattern, Fail-Closed Circuit Breaker.

### 2.2 ABLATION (The Sovereignty / Redaction Engine)
- **Role:** Surgically strips out PII, API keys, and proprietary source code before any data leaves the host (e.g., if a cloud LLM is queried).
- **Implementation:** Uses a bidirectional mapping structure (`RedactionMap`) to track original vs. redacted tokens. This allows safe "re-hydration" of data locally once the cloud LLM returns a response.
- **Pattern:** Strategy Pattern for redaction logic (Regex, NLP, Dictionary-based).
- **Constraint:** Fails closed on error.

### 2.3 TOKAMAK (The Proof / Execution Sandbox)
- **Role:** Ephemeral, isolated containment field where live Proof of Concepts (PoCs) are executed safely.
- **Implementation:** An isolated Docker container. The security payload is encapsulated as a `Command` object. If the PoC is successful, a cryptographically signed receipt (`BurhanTrace` / `TokamakTrace`) is generated.
- **Constraint:** Local Subnet Only.

---

## 3. The Cognitive Swarm (Multi-Agent System)

CHERENKOV uses an **Agent Governor** pattern to route tasks dynamically, decouple strategy from execution, and prevent context poisoning.

| Node Identity | Engine | Role | Data Access |
| :--- | :--- | :--- | :--- |
| **TENSOR** (Strategist) | Groq Llama 3.1 8B (Cloud) | Generates attack chains and plans. Breaks down compliance frameworks. | **Restricted:** Receives only sanitized breadcrumbs via ABLATION. |
| **KINETIC** (Executor) | Ollama Llama 3.2 3B (Local) | Tactical execution of exploits using TENSOR's plans. | **Full Raw Access:** Operates behind MEISSNER air-gap. |
| **AEGIS** (Arbiter) | Local Llama 3.1 8B (Local) | Arbiter and AIMD Circuit Breaker. Halts hallucination loops (e.g., KINETIC failing 3 times). | **Sanitized Context:** Reviews logic flows. |
| **LATTICE** (Memory) | Qdrant Vector DB | Long-term tactical memory, RAG, CVE knowledge base. | **Isolated:** Stores mathematical vectors of historical traces. |

---

## 4. Software Design & Internal Patterns

### 4.1 Orchestration Flow (`HybridOrchestrator`)
1. User provides target (URL/APK).
2. **Strategy:** TENSOR generates an attack chain schema.
3. **Sanitization:** Schema validated; inputs sanitized.
4. **Execution:** KINETIC executes tools/scanners based on schema.
5. **Validation:** Findings sent to TOKAMAK for isolated execution.
6. **HITL (Human-in-the-Loop):** If finding is CRITICAL, execution pauses for cryptographically signed operator approval.
7. **Finalization:** `BurhanTrace` generated, logged to WORM storage, pushed to UI.

### 4.2 Scanner Plugin Architecture
- All custom scanners must inherit from `BaseScanner` (`src/cherenkov/core/base_scanner.py`).
- This ensures auto-discovery via `ScannerRegistry`, uniform execution via `scan()`, and standardized output via `ScanResult`.

### 4.3 Key Design Patterns
- **AgentGovernor:** Central routing authority preventing context pollution.
- **AIMD Circuit Breaker (Additive Increase, Multiplicative Decrease):** Protects local LLMs (Ollama). If an API fails, allowed request rate is halved. On success, rate increases linearly.
- **Clean Architecture:** Strict separation. The Persistence Layer (`ResultStore`) is isolated from CLI/external scripts, accessed only via the API Layer (`orchestration_api.py`).

### 4.4 Data Models

**AgentState:**
```python
class AgentState(BaseModel):
    id: str
    cognitive_load: float # Current load (0.0 - 1.0)
    active_missions: List[str]
    last_trace_id: Optional[str]
    circuit_breaker_status: str # OPEN, HALF_OPEN, CLOSED
```

**BurhanTrace / TokamakTrace (Evidence Schema):**
```python
class BurhanTrace(BaseModel):
    timestamp: datetime
    finding_id: str
    poc_binary: bytes # Retained only locally
    execution_log: str
    signature: str # SHA-256(poc_binary + execution_log)
```

---

## 5. Development Standards & Best Practices

- **Security First:** Hardcoded credentials are strictly prohibited. Sensitive values must be in `.env` and validated with `hmac.compare_digest`.
- **Validation:** Pydantic schemas (v2, using `model_dump_json()`) are mandatory for all I/O between agents.
- **Testing:** Test-Driven Development (TDD) is required. >80% coverage. Tests must use `unittest.mock` to simulate external networks, ensuring testability in air-gapped environments.
- **Style:** Google Python Style Guide, strict type hints (`mypy`), `ruff`, and `black`.
- **UI System:** Frontend follows Atomic Design (Atoms: `CyberButton`, Molecules: `StatCard`, Organisms: `OperationsControl`).

---

## 6. Nomenclature / Glossary
Legacy Arabic module names are deprecated. The SSOT requires strict adherence to:
- **CHERENKOV:** Platform Namespace
- **TENSOR:** Strategy Agent
- **KINETIC:** Execution Agent
- **AEGIS:** Arbiter Agent
- **LATTICE:** Memory DB
- **TOKAMAK:** Sandbox/Validation Layer
- **MEISSNER:** Perimeter Proxy
- **ABLATION:** Redaction Engine
