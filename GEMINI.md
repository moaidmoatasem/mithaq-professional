# CHERENKOV — Gemini Agent Configuration (Jules + Antigravity)

> This file configures all Gemini-powered agents.
> **Jules** = backend/Python domain. **Antigravity** = frontend TypeScript/React domain.
> For Claude agents, see CLAUDE.md. Both files share the same architectural rules.

---

## Antigravity — Frontend Agent

**Domain (strict):** `packages/cherenkov/web/src/` only. Never touch Python or `packages/cherenkov/api/`.

### Environment
- Vite dev server: port `3000`
- Proxies to FastAPI backend: port `8000` (configured in `vite.config.ts`)
- Never hardcode `localhost:8000` — use `API_BASE` and `getWsUrl()` from `@/src/lib/api.ts`

### Import pattern
```typescript
import { API_BASE } from '@/src/lib/api';
import { useMetrics } from '@/src/hooks/useMetrics';
import { ForensicHeader } from '@/src/components/organisms/ForensicHeader';
```

### Pre-commit
```bash
cd packages/cherenkov/web
npm run lint        # tsc --noEmit
npx vite build      # production build must pass
```

### Branching
- Branch prefix: `feat/web-<issue>-<slug>`
- PR body must contain `Closes #<N>`

---

## Jules — Backend / Scanner Agent

## Environment

```
Python : 3.11 (CI) / 3.10+ (local)
Node   : 20+ (frontend only)
OS     : Ubuntu (CI) / Windows WSL2 (local dev)
```

### Setup
```bash
pip install -e ".[dev]"
```

### Test
```bash
pytest -m "not (integration or ai_generated)" --tb=short
```

### Lint + Format (Python)
```bash
ruff format packages/
ruff check packages/ --ignore W,S,B
```

### Lint + Build (Frontend)
```bash
cd packages/cherenkov/web
npm install
npm run lint        # tsc --noEmit
npx vite build
```

## Repo Layout

```
packages/cherenkov/
  api/          FastAPI server  (main.py — all /api/v1/* routes)
  core/         Domain logic    (base_scanner, circuit_breaker, tokamak, …)
  scanners/     Production-ready scanners (inherit BaseScanner)
  orchestration/Workflow engine
  web/src/      React 19 + Vite + Tailwind v4 dashboard
  autonomous_generated/  Raw AI output — do not import directly

tests/          pytest suite (unit + integration markers)
scripts/        Autonomous pipeline scripts
.github/        CI workflows + Claude/Jules actions
```

## Architectural Invariants (Non-Negotiable)

1. **Zero-egress (MEISSNER):** No outbound calls outside the scan target. All LLM calls go through local Ollama or gated Groq. Never add `requests.get(<external_url>)` in core logic.
2. **ABLATION:** Any payload sent to an LLM API must pass through `cherenkov.core.ablation` to redact PII/secrets.
3. **TOKAMAK signing:** Every PoC execution result must carry `trace_hash = sha256(output + timestamp)`.
4. **Shred receipts:** Temp file cleanup = cryptographic overwrite + JSON receipt. No bare `os.remove()`.

## Import Convention

```python
# Correct
from cherenkov.core.base_scanner import BaseScanner, ScanResult, Finding, Severity
from cherenkov.core.circuit_breaker import CircuitBreaker

# Wrong — do not use
from src.cherenkov.X import Y
```

## Branching

- Branch: `feat/<issue-number>-<slug>` | `fix/<issue-number>-<slug>`
- PR base: `main`
- Reference issue: body must contain `Closes #<N>`
- Never push to `main` directly

## Key GitHub Issues (active work)

| # | What | Priority |
|---|---|---|
| [#174](https://github.com/moaidmoatasem/cherenkov-professional/issues/174) | TOKAMAK Docker sandbox | high |
| [#175](https://github.com/moaidmoatasem/cherenkov-professional/issues/175) | HITL approval gate | high |
| [#176](https://github.com/moaidmoatasem/cherenkov-professional/issues/176) | Compliance mapper + SARIF/PDF | medium |
| [#177](https://github.com/moaidmoatasem/cherenkov-professional/issues/177) | SQLite WAL + real health metrics | high |
| [#178](https://github.com/moaidmoatasem/cherenkov-professional/issues/178) | Graduate 5 scanners to BaseScanner | medium |
