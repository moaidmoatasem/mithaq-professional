# CHERENKOV — Architecture

## Canonical Layout

```
cherenkov-professional/
├── packages/cherenkov/          ← ALL Python source (canonical root)
│   ├── api/main.py              ← FastAPI server, REST + WebSocket
│   ├── core/
│   │   ├── base_scanner.py      ← BaseScanner ABC, Severity/Finding/ScanResult
│   │   ├── circuit_breaker.py   ← MEISSNER AIMD circuit breaker
│   │   ├── engine.py            ← ScanEngine — parallel asyncio orchestration
│   │   ├── registry.py          ← ScannerRegistry — registered scanner list
│   │   ├── tokamak.py           ← TOKAMAK Docker sandbox (P0 — not yet wired)
│   │   └── storage/database.py  ← SQLite WAL helpers
│   ├── scanners/                ← Graduated BaseScanner implementations
│   ├── compliance/              ← ComplianceMapper — CWE → OWASP/SAMA/EGY-FIN/DORA
│   ├── agents/                  ← AI agent connectors (TENSOR, KINETIC)
│   ├── ai/ablation/             ← ABLATION redactor / PII sanitizer
│   └── web/                     ← React 19 / Vite / Tailwind v4 frontend
│       └── src/
│           ├── lib/api.ts        ← API_BASE, getWsUrl() — single source of truth
│           ├── hooks/            ← useMetrics, useLiveEvents, usePendingApprovals
│           └── components/organisms/
├── tests/
│   ├── unit/
│   └── integration/
├── deploy/docker-compose.yml    ← Production stack (Ollama + Qdrant + app)
└── .agents/                     ← Agent coordination
    ├── context.md               ← Universal onboarding for all agents
    └── tasks/issue-N.md         ← Per-issue implementation briefs
```

## The Trident

| System | Role | Status |
|---|---|---|
| **MEISSNER** | AIMD circuit breaker — fail-closed network perimeter | ✅ `core/circuit_breaker.py` |
| **ABLATION** | PII redactor — scrubs payloads before any LLM call | ✅ `ai/ablation/` |
| **TOKAMAK** | Docker sandbox — executes PoC, SHA-256 trace signing | ⚠️ stub — P0 issue #222 |

## AI Stack

| Component | Model | Role |
|---|---|---|
| TENSOR | Qwen2.5-Coder 7B (Ollama) | Primary reasoning / scanner generation |
| KINETIC | Qwen2.5-Coder 1.5B (Ollama) | Autocomplete / fast triage |
| LATTICE | nomic-embed-text + Qdrant (local) | Adaptive memory — P0 issue #224 |

## Import Convention

```python
# CORRECT
from cherenkov.core.base_scanner import BaseScanner, Finding, Severity
from cherenkov.core.circuit_breaker import meissner_hub

# WRONG — never use
from src.cherenkov.core.base_scanner import BaseScanner
```

## Compliance Targets

- **EGY-FIN CSF** — Egyptian Financial Sector Cybersecurity Framework (CBE mandate)
- **SAMA CSF** — Saudi Arabia Monetary Authority Cybersecurity Framework
- **DORA** — EU Digital Operational Resilience Act
- **OWASP Top 10** — Web application security

## Current Phase

**Phase 2 in progress** — see [roadmap](docs/development/roadmap-detailed.md) and open issues.

P0 blockers: [#221](https://github.com/moaidmoatasem/cherenkov-professional/issues/221) (health), [#222](https://github.com/moaidmoatasem/cherenkov-professional/issues/222) (TOKAMAK), [#223](https://github.com/moaidmoatasem/cherenkov-professional/issues/223) (root cleanup), [#224](https://github.com/moaidmoatasem/cherenkov-professional/issues/224) (LATTICE).
