# CHERENKOV Sovereign Security | Product Roadmap

This document outlines the strategic roadmap for CHERENKOV, ensuring alignment with sovereign security standards, autonomous agent execution, and strict human-in-the-loop (HITL) requirements for critical operations.

## Phase 1: Foundation & Sovereignization (Current State)
* **Goal**: Establish the "Trident of Truth" architecture.
* **Deliverables**:
    * Core network enforcement layer (DAREE3).
    * Data redaction engine (SIYAADA) using bidirectional hashing.
    * Initial forensic validation sandbox (AL-BURHAN).
    * Restoration of high-fidelity UI.
* **Milestone**: Version 1.0.0-rc1

## Phase 2: Swarm Optimization & Parallelism (Next 3 Months)
* **Goal**: Enable fully concurrent AI agent orchestration while maintaining cognitive separation.
* **Deliverables**:
    * Parallel execution of agents via `Asyncio` task orchestration.
    * Dynamic resource slotting (CPU/NPU detection).
    * Implementation of `BaseScanner` interface for all candidate security scanners.
    * AIMD circuit breakers for robust LLM inference.
* **Milestone**: Version 1.1.0

## Phase 3: Production Hardening, Compliance & HITL Enforcement (Months 3-6)
* **Goal**: Cement CHERENKOV as an enterprise-grade sovereign security tool with legally binding evidence generation.
* **Deliverables**:
    * Automated Compliance-as-Code (mapping to SAMA CSF, EGY-FIN CSF, DORA).
    * WORM (Write Once Read Many) SQLite audit vault.
    * Implementation of Human-in-the-Loop workflows for HIGH/CRITICAL vulnerabilities.
    * Enterprise SSO/RBAC for the local portal.
* **Milestone**: Version 1.5.0

## Phase 4: Advanced Exploitation & Mobile Triage (Months 6-12)
* **Goal**: Support robust mobile application security auditing (Android/iOS) and advanced exploit chains.
* **Deliverables**:
    * Full integration of Mobile Scanners (APKTool, Androguard wrappers).
    * Frida hook generation.
    * Drozer PoC Executor under AL-BURHAN sandbox.
* **Milestone**: Version 2.0.0

## Phase 5: Ecosystem Integration (Future)
* **Goal**: Plug into existing enterprise SIEMs without violating zero-egress.
* **Deliverables**:
    * Local PDF & SARIF report generation.
    * CI/CD integration using local GitHub Actions runners.
* **Milestone**: Version 2.5.0
