# Changelog

## v1.0.0 — MITHAQ Sovereign Security Standard (May 2026)

### Added
- **Trident of Truth Architecture**: Implemented DAREE3 (Shield), SIYAADA (Sovereignty), and AL-BURHAN (Proof) boundaries.
- **Atomic Design Portal**: Fully restructured high-fidelity web dashboard using Atomic Design principles.
- **Forensic MITHAQ Trace**: Implemented cryptographic signing (SHA-256) for all security findings.
- **Master Sovereign Blueprint**: Comprehensive architectural and roadmap documentation.
- **Code of Conduct & Contributing Guidelines**: Established formal sovereign development standards.

### Changed
- **Global Rebranding**: Full migration from legacy DAQIQ namespace to MITHAQ.
- **CI/CD Stabilization**: Upgraded GitHub actions to CodeQL v3 and enforced strict permission models.
- **Core Orchestration**: Refactored `HybridOrchestrator` to enforce modular security boundaries.


## v0.1.1 — Security Patch (May 2026)

### Fixed
- CRITICAL: Flask debug mode disabled; server binds to localhost by default (env-configurable)
- CRITICAL: Stored XSS in web dashboard via unescaped innerHTML — all dynamic values now escaped
- HIGH: Bare `except:` handlers replaced with typed exception handling in all scanner files
- HIGH: URL validation added to `SimpleScanner.__init__` — rejects non-http/https schemes
- HIGH: Server-side URL validation added to `/api/scan` endpoint

## v0.1.0-alpha — Initial Release (May 2026)

### Added
- Basic HTTP security header scanner
- HTTP methods scanner (PUT, DELETE, TRACE, CONNECT detection)
- HTTPS/HTTP detection
- Flask web dashboard (localhost only from v0.1.1)
- Basic CLI (`mithaq_cli.py`)

