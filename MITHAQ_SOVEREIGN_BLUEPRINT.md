# CHERENKOV Sovereign Security | Master Blueprint & Technical Roadmap

**Revision: 1.2 | Status: Phase 1 Finalized | Classification: Sovereign Strategic Asset**

---

## 1. Project Status Summary
CHERENKOV has transitioned from a legacy architecture into a **Sovereign Security Standard**. 
- **Namespace Rebranded**: Global transition from CHERENKOV to CHERENKOV.
- **Architectural Enforcement**: The "Trident of Truth" (MEISSNER, ABLATION, TOKAMAK) is now hardcoded into the orchestrator logic.
- **UI/UX Restoration**: High-fidelity dashboard restored using Atomic Design principles.
- **CI/CD Stabilization**: GitHub security scans fixed with upgraded CodeQL v3 and strict permission models.

---

## 2. System Architecture (The Trident of Truth)

### **Layer 1: MEISSNER (The Shield)**
- **Type**: Network Enforcement Layer.
- **Pattern**: Fail-Closed Circuit Breaker.
- **Logic**: Nginx/Docker-level isolation that drops all unauthorized outbound traffic.
- **Design Pattern**: **Proxy Pattern** for request interception and **Circuit Breaker** (AIMD) for agent communication resilience.

### **Layer 2: ABLATION (Sovereignty)**
- **Type**: Data Sanitization & Redaction Engine.
- **Pattern**: **Strategy Pattern** for redaction logic (Regex, NLP, Dictionary-based).
- **Data Structure**: `RedactionMap` (A bidirectional hash map tracking original vs. redacted tokens for reconstruction in local-only nodes).

### **Layer 3: TOKAMAK (The Proof)**
- **Type**: Forensic Validation & TOKAMAKing.
- **Pattern**: **Command Pattern** for executing security payloads.
- **Data Structure**: `TokamakTrace` (A Pydantic model encapsulating proof execution details, logs, and a SHA-256 cryptographic signature).

---

## 3. Design Patterns & Engineering Excellence

### **Cognitive Patterns**
- **Multi-Agent Orchestration (Swarm Architecture)**: Decoupling strategy (Al-Muhandis) from execution (Al-Munafeedh) to prevent context poisoning.
- **AIMD Circuit Breaker**: Prevents agent cascades during high latency or API failures.
- **Memory RAG**: Local Qdrant instance for dialect-aware retrieval and CVE mapping.

### **Frontend Design Pattern: Atomic Design**
- **Atoms**: `CyberButton`, `CyberBadge`, `PulseDot`.
- **Molecules**: `StatCard`, `VulnCard`.
- **Organisms**: `OperationsControl`, `ThreatIntelPanel`.
- **Templates**: `MainLayout`.
- **Rationale**: Ensures high-fidelity UI reuse and separation of concerns between visual logic and operational stream.

### **Security Best Practices**
- **Zero-Egress by Default**: All sensitive computation remains on local hardware.
- **Forensic Integrity**: Every finding is cryptographically signed and auditable.
- **Compliance Alignment**: Hardcoded checks for EGY-FIN CSF and SAMA CSF frameworks.

---

## 4. Data Structures

### **Agent State Vector**
```python
class AgentState(BaseModel):
    id: str
    cognitive_load: float  # 0.0 to 1.0
    active_missions: List[str]
    last_trace_id: Optional[str]
    circuit_breaker_status: str  # OPEN, HALF_OPEN, CLOSED
```

### **TokamakTrace (Evidence Schema)**
```python
class TokamakTrace(BaseModel):
    timestamp: datetime
    finding_id: str
    poc_binary: bytes  # Local-only
    execution_log: str
    signature: str  # SHA-256(poc_binary + execution_log)
```

---

## 5. Development Roadmap & Phases

### ✅ **Phase 1: Foundation & Sovereignization (COMPLETED)**
- [x] Global Namespace Rebrand (CHERENKOV -> CHERENKOV).
- [x] Trident Architecture Implementation.
- [x] ABLATION Redaction Engine Stabilization.
- [x] High-Fidelity UI Restoration (Atomic Design).
- [x] CI/CD Security Pipeline Fixes.

### 🚀 **Phase 2: Swarm Optimization & Parallelism (IN PROGRESS)**
- [ ] **Parallel Agent Execution**: Implement `Asyncio` task orchestration for simultaneous scanning.
- [ ] **Slotting Logic**: Dynamic resource allocation for agent swarm based on local hardware capability.
- [ ] **AIMD Refinement**: Fine-tune multiplicative decrease triggers for local LLM inference.
- [ ] **Mobile & Web Scanners Integration**: Formalize `BaseScanner` interface for all sub-modules.

### 🛡️ **Phase 3: Production Hardening & Compliance**
- [ ] **compliance-as-code**: Automated mapping of findings to SAMA/DORA control IDs.
- [ ] **Forensic Audit Vault**: Local-only SQLite WORM (Write Once Read Many) storage for traces.
- [ ] **Enterprise SSO/RBAC**: Zero-trust access control for the local portal.

---

## 6. Action Items & Next Missions

1. **Mission: Parallel Swarm Orchestration**
   - Refactor `HybridOrchestrator` to support concurrent agent missions.
   - Implement hardware-aware slotting (CPU/NPU detection).

2. **Mission: Scanner Formalization**
   - Migrate all candidate scanners into `src/cherenkov/scanners/` using the `BaseScanner` class.
   - Enforce TOKAMAK proof validation for each scanner type.

3. **Mission: Documentation Deep-Dive**
   - Finalize `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md` with "Sovereign-First" guidelines.
   - Generate technical API documentation for the internal agent communication protocol.

---

**CHERENKOV: Accuracy is the root of sovereignty.**
