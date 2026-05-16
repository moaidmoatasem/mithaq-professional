# Scanners

CHERENKOV's scanning engine uses a plugin-based architecture. All scanners inherit from `BaseScanner` and are auto-discovered via the `ScannerRegistry`.

## Key Concepts

- **Plugin Architecture** — Drop-in scanner modules with standard interfaces
- **Auto-Discovery** — Scanners are automatically registered at startup
- **Chainable** — Scanners can compose and pipeline results
- **Validation Gate** — Every result passes through TOKAMAK proof validation
