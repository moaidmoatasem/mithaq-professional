# MITHAQ Releases Strategy

This document maps the internal roadmap to public GitHub releases.

## v1.0.0-rc1: Sovereign Foundation (Completed)
*   **Tag:** `v1.0.0-rc1`
*   **Features:**
    *   DAREE3 Network Proxy enabled.
    *   SIYAADA Redaction engine stabilized.
    *   AL-BURHAN proof validation concept introduced.
    *   Transitioned namespace from DAQIQ to MITHAQ.
*   **Target Audience:** Early adopters testing air-gapped environments.

## v1.1.0: Swarm Concurrency
*   **Tag:** `v1.1.0` (Target: +1 Month)
*   **Features:**
    *   `Asyncio` parallel execution in `HybridOrchestrator`.
    *   AIMD Circuit Breaker for Ollama integration.
    *   Implementation of `BaseScanner` interface.
*   **Notes:** This release marks the transition from sequential execution to a true agent swarm.

## v1.5.0: Enterprise Validation & HITL
*   **Tag:** `v1.5.0` (Target: +3 Months)
*   **Features:**
    *   Mandatory Human-in-the-Loop workflows for CRITICAL findings.
    *   WORM SQLite audit logging for legally binding execution receipts.
    *   Compliance mapping (SAMA, EGY-FIN).
*   **Notes:** This is the first "Enterprise Ready" tag.

## v2.0.0: The Mobile Triad
*   **Tag:** `v2.0.0` (Target: +6 Months)
*   **Features:**
    *   Full Android/iOS static and dynamic analysis.
    *   APKTool, Androguard, and Frida integration.
*   **Notes:** Expands MITHAQ from web/network scanning to deep mobile forensics.
