# Changelog

## v1.0.0-rc2 — Documentation Finalization (May 2026)

### Added
- **Full mkdocs alignment**: All root-level project docs migrated into `docs/` structure
- **Architecture Overview**: `docs/architecture/overview.md` — Clean Architecture & Agent Governor
- **Design Docs**: `docs/development/design.md`, `docs/development/design-system.md` — brand tokens, Atomic components
- **Technical Specification**: `docs/development/technical-specification.md` — full system blueprint
- **Premortem Analysis**: `docs/development/premortem.md` — 10 failure modes with prevention
- **SSOT**: `docs/architecture/ssot.md` — Single Source of Truth for Cognitive Swarm
- **Sovereign Blueprint**: `docs/development/sovereign-blueprint.md` — master roadmap
- **Master Plan**: `docs/development/master-plan.md` — 30-week project overview
- **Releases & Newsletter**: `docs/development/releases.md`, `docs/development/newsletter-concept.md`
- **Wiki Index**: `docs/development/wiki-index.md` — cross-reference to GitHub wiki

### Changed
- **Nav fully aligned**: Every doc page in `docs/` included in `mkdocs.yml` nav — zero orphan pages
- **`site/` build artifacts untracked**: Removed 68 stale files from git tracking (`.gitignore` already in place)
- **Cross-references fixed**: All `github/RELEASES.md` links updated to `development/releases.md`

### Removed
- Stale GitHub issue doc pages: `docs/github/issues/001`, `002`, `003`
- Empty `docs/github/` directory

## v1.0.0 — CHERENKOV Sovereign Security Standard (May 2026)

### Added
- **Trident of Truth Architecture**: Implemented MEISSNER (Shield), ABLATION (Sovereignty), and TOKAMAK (Proof) boundaries.
- **Atomic Design Portal**: Fully restructured high-fidelity web dashboard using Atomic Design principles.
- **Forensic CHERENKOV Trace**: Implemented cryptographic signing (SHA-256) for all security findings.
- **Master Sovereign Blueprint**: Comprehensive architectural and roadmap documentation.
- **Code of Conduct & Contributing Guidelines**: Established formal sovereign development standards.

### Changed
- **Global Rebranding**: Full migration from legacy CHERENKOV namespace to CHERENKOV.
- **CI/CD Stabilization**: Upgraded GitHub actions to CodeQL v3 and enforced strict permission models.
- **Core Orchestration**: Refactored `HybridOrchestrator` to enforce modular security boundaries.


## [0.1.2] - 2026-05-08
### Fixed
- Critical `eval()` injection vulnerability in `VulnerabilitySeverityScore` scanner.
- Cross-platform test failure for vulnerability scanners.

### Added
- Cloudflare Workers configuration (`wrangler.jsonc`) for deployment.

## [0.1.1] - 2026-05-08
Security Patch (May 2026)

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
- Basic CLI (`cherenkov_cli.py`)

