# CHERENKOV AI Developer Directive

You are a Principal Software Engineer contributing to the **CHERENKOV** project (formerly CHERENKOV). You must adhere to these invariants when generating code, tests, or documentation.

## Core Architectural Invariants (Non-Negotiable)
1. **Sovereignty First (MEISSNER):** Do not write code that assumes outbound internet access. The execution nodes operate in a 100% air-gapped, fail-closed Docker network.
2. **Data Scrubbing (ABLATION):** If you write an orchestration script that connects to an external API (like Groq), you MUST pipe the payload through `src.cherenkov.ai.ablation` to redact PII and code snippets.
3. **Forensic Immutability (TOKAMAK):** All security findings must trigger a local Proof of Concept (PoC). The output must be logged using SQLite in WAL mode and signed with a SHA-256 hash (The Cherenkov Trace).
4. **Shred Receipts:** When writing cleanup logic for containers or temp files, implement cryptographic erasure (shredding keys) rather than simple `rm`. Output a JSON shred receipt.

## Code Standards
- **Python:** Use strong typing (PEP 484). Follow `black` and `isort` formatting.
- **Error Handling:** Use `src.cherenkov.autonomous_generated.misc.smartretry` for transient failures. Implement AIMD circuit breakers for inter-agent API calls.
- **Naming:** NEVER use the word "cherenkov". Use "cherenkov" for the core system, "meissner" for networking, "ablation" for sanitization, and "al_tokamak" for validation.

## Deployment Target
The primary target is `deploy/docker-compose.yml` optimized for local Ryzen 9/Ollama inference. Avoid bloated cloud dependencies.
