# CLAUDE.md — CHERENKOV Per-Session SSOT

> Read this first, every session. Then read [`AGENTS.md`](./AGENTS.md) for multi-agent coordination rules.

## Token discipline

- **Grep before Read.** Never open a file without knowing the target line. Know the path → `Grep pattern file` or `Read offset+limit`. Don't know → `Glob` or one `Explore` agent.
- **Never read speculatively:** `node_modules/`, `venv/`, `__pycache__/`, `data/`, `logs/`, `workflow_results/`, `assets/`, `cherno-docs/` — large or generated, read only if the task names a specific file inside.
- **Subagent discipline.** Only spawn for genuinely parallel work. Pass file:line refs in the prompt.
- **End of turn:** one sentence — what changed, what's next.

## Product (one paragraph)

CHERENKOV is a sovereign AI security platform for MENA financial institutions. It produces **cryptographically proven, sovereignty-preserving, regulator-ready** security evidence: scanners surface findings, TOKAMAK confirms them via isolated PoC execution, every result is SHA-256 signed (CherenkovTrace) and mappable to EGY-FIN CSF controls. No data leaves the customer perimeter unless ABLATION sanitizes it first.

## Start command

```bash
source venv/bin/activate
export CHERENKOV_JWT_SECRET=cherenkov-sovereign-audit-key-2024
export PYTHONPATH=$PYTHONPATH:$(pwd)/packages
uvicorn cherenkov.api.main:app --host 0.0.0.0 --port 8000
```

## Non-negotiable rules

1. **Never commit to `main`.** Always branch → PR → Moaid merges. Branch protection enforced.
2. **Package path is `packages/cherenkov/` — never `src/`.** Imports: `from cherenkov.X import Y`.
3. **MEISSNER:** assume zero outbound internet. Fail closed.
4. **ABLATION:** any payload leaving the perimeter must pass through `cherenkov.ai.ablation` to redact PII and code.
5. **TOKAMAK:** HIGH/CRITICAL findings are unconfirmed until a real PoC executes in an isolated container and the output is SHA-256 signed.
6. **CherenkovTrace:** every scan result is hashed and stored. RFC 3161 timestamping uses `freetsa.org` only.
7. **Shred Receipts:** container/temp cleanup uses cryptographic erasure (shred keys), not `rm`. Emit JSON receipt.
8. **Per-PR budget:** ≤8 files, ≤400 lines (excluding lockfiles). Larger splits stack.
9. **Touch only your domain** (see AGENTS.md §1f and `.agentsignore`).
10. **Open a claim ticket** (`gh issue create -l claim/active`) before editing — prevents agent collisions.

## Canonical names

| Term | Meaning |
|---|---|
| **MEISSNER** | Zero-egress network boundary |
| **ABLATION** | Data sanitization layer before any external LLM call |
| **TOKAMAK** | PoC execution sandbox; produces SHA-256 cryptographic proof |
| **LATTICE** | Qdrant vector memory of scan history (embeddings via `nomic-embed-text`) |
| **TENSOR** | Cloud LLM tier (only reachable through ABLATION) |
| **KINETIC** | Local Ollama LLM tier (raw data permitted) |
| **CherenkovTrace** | SHA-256 + RFC 3161 signed evidence record |

## Current state (honest)

| Component | Status |
|---|---|
| Auth (JWT) | ✅ working |
| Scan endpoint vs DVWA | ✅ returns 29 raw findings |
| WebSocket `/ws/live` | ✅ live |
| LiteLLM proxy (port 4000) | ✅ live with `code-smart`, `embed`; `architect`/`red-team` pending model pulls |
| Findings deduplication | ❌ not implemented |
| LATTICE wired to scan output | ❌ bridge exists, not called |
| TOKAMAK live PoC execution | ❌ schema only, no Docker spawn |
| Architect / Red Team / SecOps agents | ❌ not implemented |
| CherenkovTrace signing on scan | ❌ not wired |
| EGY-FIN CSF mapping | ❌ not started |

## Key file paths

```
packages/cherenkov/api/main.py              ← FastAPI entry, scan endpoint
packages/cherenkov/core/tokamak.py          ← PoC execution (schema only)
packages/cherenkov/core/circuit_breaker.py  ← MEISSNER (partial)
packages/cherenkov/core/ablation/           ← ABLATION sanitizers
packages/cherenkov/ai/lattice_bridge.py     ← Qdrant embed/store
packages/cherenkov/agents/                  ← Architect/RedTeam/SecOps (TBD)
packages/cherenkov/web/                     ← Vite dashboard (Antigravity domain)
docs/AGENT_PROMPTS.md                       ← Canonical agent prompts (this work)
```

## Service URLs

| Service | URL | Credentials / start |
|---|---|---|
| API | http://localhost:8000 | `admin` / `admin` |
| LATTICE (Qdrant) | http://localhost:6333 | `docker start qdrant` |
| DVWA target | http://localhost:80 | `docker compose -f deploy/dvwa-compose.yml up -d` |
| Ollama | http://localhost:11434 | `systemctl start ollama` |
| LiteLLM proxy | http://localhost:4000 | `bash ~/start-litellm.sh` (key: `sk-local-dev`) |

## Model routing (via LiteLLM)

| Alias | Backing model | Role |
|---|---|---|
| `architect` | `foundation-sec-8b-reasoning` | Engagement planning, reasoning |
| `red-team` | `redsage-dpo` (or WhiteRabbitNeo) | Offensive task generation |
| `code-smart` | `qwen2.5-coder:7b` | Code automation |
| `embed` | `nomic-embed-text` | LATTICE embeddings |
| `cloud-fallback` | `groq/llama-3.1-8b-instant` | TENSOR tier (ABLATION-gated) |

## Agent assignments

| Agent | Owns | Forbidden |
|---|---|---|
| **Jules** | API, scanners, tests, CI, single-file fixes | `packages/cherenkov/web/`, `docs/architecture/` |
| **Claude Code** | Architecture, agent layer, multi-file refactors | `packages/cherenkov/web/`, `.github/workflows/` (without explicit task) |
| **Antigravity** | `packages/cherenkov/web/` only | Anything Python |
| **Autonomous Pipeline** | `packages/cherenkov/autonomous_generated/scanners/` | Anything else |
| **Moaid** | Merge authority, releases, CBE coordination | Writing code |

See AGENTS.md for the full matrix, claim-ticket protocol, and worktree rules.

## Branch & commit format

```
<type>/<issue#>-<slug>           feat/42-tokamak-docker-sandbox
<type>(<scope>): <description> (#<issue>)
Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

## Immediate priority (current session)

Phase 2 wiring — in this exact order, one PR per step:

1. Deduplicate scan findings by `(cwe, type)` — `packages/cherenkov/api/main.py`
2. Wire LATTICE `embed_and_store` after each scan (non-blocking)
3. TOKAMAK live PoC execution (docker-py)
4. Security Architect agent (`packages/cherenkov/agents/architect.py`)
5. CherenkovTrace SHA-256 signing on scan completion
6. EGY-FIN CSF mapping → Cairo pilot

Issues created in GitHub. Pick the next P0/P1 in your domain.
