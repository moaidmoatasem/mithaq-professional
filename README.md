# MITHAQ (ميثاق) | The Sovereign Security Standard
**Precision in Sovereignty (الدقة في السيادة)**

MITHAQ is an air-gapped, sovereign AI security and quality intelligence platform. Designed explicitly for highly regulated infrastructures (EGY-FIN CSF, SAMA CSF, DORA), it tests traditional software, mobile applications, and embedded AI systems entirely on local hardware.

MITHAQ operates on a mathematically provable "Trident of Truth": it finds vulnerabilities, proves them with non-destructive local execution, and cryptographically signs the evidence—without your source code, credentials, or customer data ever leaving your hardware.

---

## 🛡️ The Trident Architecture

The platform divides cognitive execution across a highly restricted multi-agent swarm, governed by strict physical and cryptographic boundaries.

### 1. DAREE3 (The Shield)
The fail-closed network perimeter. DAREE3 drops all unauthorized outbound connections, physically severing local execution nodes from the external internet to enforce absolute zero-egress.

### 2. SIYAADA (Sovereignty)
The redaction engine. In hybrid configurations, any data requiring cloud processing is forced through SIYAADA, which strips all PII, credentials, and proprietary code before egress is permitted.

### 3. AL-BURHAN (The Proof)
The validation sandbox. No HIGH/CRITICAL finding is reported without Al-Burhan executing a live, non-destructive Proof of Concept (PoC) against the target.

### 📜 Mithaq Trace & Evidence Governance
Every action is recorded via SQLite WAL/WORM storage and signed with a SHA-256 cryptographic hash. This generates legally binding **Shred Receipts** for compliance audits, proving both the vulnerability and the subsequent cryptographic erasure of the test data.

---

## 🚀 Quick Start (Air-Gapped Local Deployment)

MITHAQ is built for Docker-native, offline execution. 

```bash
# 1. Clone the repository
git clone https://github.com/moaidmoatasem/mithaq-professional.git
cd mithaq-professional

# 2. Configure environment (No external APIs required)
cp .env.example .env

# 3. Initialize the DAREE3 perimeter and local Ollama swarm
bash launch_perfection.sh
```

## ⚖️ Licensing & The Ethical Open-Core
We refuse to utilize the "SSO Wall of Shame." Core security features (SSO, RBAC, audit logging, local scanning) are provided under **MIT/Apache**. The proprietary multi-agent orchestrator and advanced Arabic RTL/OCR modules are dual-licensed (**AGPLv3/BSL**) to protect localized intelligence from hyperscaler cannibalization.

---
*Internal Ref: MTH-9941-R | Status: Phase 1 Enforced*
