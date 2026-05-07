# Changelog

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

