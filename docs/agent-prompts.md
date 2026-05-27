# CHERENKOV — Canonical Agent Prompts

> SSOT for every AI agent session (Jules, Claude Code, Antigravity, Aider, Open WebUI).
> Paste the **Context Block** at the start of every session, then the section
> matching your task. Branch and PR per the rules in [`../AGENTS.md`](../AGENTS.md).

---

## Context Block — paste at start of every session

```
PROJECT: CHERENKOV sovereign AI security platform
REPO: git@github.com:moaidmoatasem/cherenkov-professional.git
BRANCH RULE: Never commit to main. Branch → PR → Moaid merges.
PACKAGE: packages/cherenkov/ (NEVER src/)
IMPORTS: from cherenkov.X import Y
VENV: source ~/cherenkov-professional/venv/bin/activate
ENV: export CHERENKOV_JWT_SECRET=cherenkov-sovereign-audit-key-2024
PYTHONPATH: export PYTHONPATH=$PYTHONPATH:$(pwd)/packages

SERVICES:
  API:     http://localhost:8000 (admin/admin)
  LATTICE: http://localhost:6333 (docker start qdrant)
  DVWA:    http://localhost:80   (docker compose -f deploy/dvwa-compose.yml up -d)
  Ollama:  http://localhost:11434
  LiteLLM: http://localhost:4000 (bash ~/start-litellm.sh, key: sk-local-dev)

ARCHITECTURE:
  MEISSNER → zero egress
  ABLATION → PII strip before cloud LLM
  TOKAMAK  → PoC execution (Kali container, SHA-256 proof)
  LATTICE  → Qdrant vector memory (nomic-embed-text)
  TENSOR   → cloud LLM (sanitized only, via ABLATION)
  KINETIC  → local Ollama (raw data OK)
  CherenkovTrace → SHA-256 + RFC 3161 signed evidence

MODEL ROUTING (via LiteLLM at port 4000):
  architect  → Foundation-Sec-8B-Reasoning
  red-team   → RedSage-DPO / WhiteRabbitNeo
  code-smart → qwen2.5-coder:7b
  embed      → nomic-embed-text
```

---

## Section index

| § | Task | Target agent | Branch prefix |
|---|---|---|---|
| 1A | Update CLAUDE.md (per-session SSOT) | Claude Code | `docs/` |
| 1B | Update AGENTS.md (agent roster) | Claude Code | `docs/` |
| 1C | Architecture docs refresh | Claude Code | `docs/` |
| 1D | DIFFERENTIATION.md (market positioning) | Claude Code | `docs/` |
| 2A | Dashboard FE — agent status panel | **Antigravity only** | `feat/web-` |
| 2B | Scan response schema (proof chain fields) | Jules / Claude Code | `feat/` |
| 3A | Security Architect agent layer | Jules / Claude Code | `feat/` |
| 3B | TOKAMAK live PoC execution | Jules | `feat/` |
| 3C | LATTICE bridge wiring to scan | Jules | `feat/` |
| 3D | Red Team + SecOps agent stubs | Claude Code | `feat/` |
| 4  | GitHub issues batch (work queue) | Jules (one-shot) | n/a |
| 5  | Jules session queue (sequenced) | Jules | per-session |
| 6  | Claude Code multi-file wiring session | Claude Code | `feat/` |
| 7  | Open WebUI system preset | Open WebUI (save once) | n/a |

---

## 1A — Rewrite CLAUDE.md

> CLAUDE.md must be ≤120 lines. One-paragraph product description, start
> command, non-negotiable rules (≤10), canonical names table, honest
> current-state matrix, key file paths (≤10 lines), service URLs, model
> routing table, agent assignments, branch/commit format, immediate priority.

Read current `CLAUDE.md`, preserve what's accurate, fix what's wrong, remove
fluff. Branch: `docs/update-claude-md`. Open PR.

---

## 1B — Rewrite AGENTS.md

Define per agent: domain (allowed paths), forbidden (denied paths), trigger
(when invoked), model (which LLM), branch format. Cover human operator,
Jules, Claude Code, Antigravity, Aider, Cline, plus the planned runtime
agents (Security Architect, Red Team, SecOps).

Include sections for branch protection, worktree pattern,
[`.agentsignore`](../.agentsignore) boundaries, commit co-authorship.

Branch: `docs/update-agents-md`. Open PR.

---

## 1C — Architecture docs refresh

Update `docs/architecture/`:

- `hld-diagram.md`: three-tier diagram (Core / Dual Brain / Agents).
- `ssot.md`: LiteLLM proxy as routing layer; phase status.
- `trident.md`: MEISSNER / ABLATION / TOKAMAK current implementation status.

Branch: `docs/architecture-update`. Open PR.

---

## 1D — Create DIFFERENTIATION.md

`docs/strategy/DIFFERENTIATION.md` — one-sentence core differentiator, why
CHERENKOV wins against cloud SAST/DAST, Pentera/Cymulate, OWASP ZAP, human
consultants; Trident-of-Truth for non-technical audience; AI-era
differentiators; MENA market specifics (EGY-FIN CSF, Arabic PDF, CBE).

Branch: `docs/differentiation-strategy`. Open PR.

---

## 2A — Dashboard FE (Antigravity ONLY)

Domain: `packages/cherenkov/web/src/` only. **Do not touch any Python.**

Changes:
1. Agent status panel (Architect / Red Team / SecOps with model name + state).
2. Health nodes display: add `architect`, `red-team`, `secops`.
3. LiteLLM proxy status indicator (port 4000 reachable, active model count).
4. Scan results: dedup toggle, CherenkovTrace hash column, TOKAMAK status per finding.
5. Branding: remove any DAQIQ references, header reads `CHERENKOV // SECURITY OPERATIONS CENTER`, version `v0.2.0-beta`.

Rebuild: `npm run build && cp -r dist/* ../api/static/`.
Branch: `feat/web-dashboard-agent-status`. Open PR.

---

## 2B — Scan response schema

In `packages/cherenkov/api/main.py`, extend the response Pydantic models:

```python
class Finding(BaseModel):
    scanner: str
    title: str
    type: str
    severity: str
    cwe: str
    description: str
    remediation: str
    confirmed: bool = False
    proof_hash: Optional[str] = None
    trace_id: Optional[str] = None
    false_positive: bool = False

class ScanResult(BaseModel):
    scan_id: str
    target: str
    timestamp: str
    vulnerabilities: list[Finding]
    count: int
    trace_hash: Optional[str] = None
    signed_at: Optional[str] = None
```

Dedup by `(cwe, type)` before returning. Update tests.
Branch: `feat/scan-schema-proof-chain`. Open PR.

---

## 3A — Security Architect agent

Create `packages/cherenkov/agents/architect.py` with `SecurityArchitect` class
and `EngagementPlan` dataclass. All calls go through LiteLLM
(`http://localhost:4000`, model alias `architect`). Add
`POST /api/v1/architect/plan` accepting `{target, framework}`. Mock HTTP in
tests. Branch: `feat/architect-agent`. Open PR.

Reference implementation in the source prompts document (§3A).

---

## 3B — TOKAMAK live execution

Wire `execute_poc()` in `packages/cherenkov/core/tokamak.py` to spawn a real
Docker container with `network_mode="none"` (MEISSNER), capture logs, SHA-256
hash them on success, remove container with `force=True, v=True`. Plug into
the scan pipeline for HIGH/CRITICAL findings.

Branch: `feat/tokamak-live-execution`. Open PR.

---

## 3C — LATTICE bridge wiring

After every completed scan in `packages/cherenkov/api/main.py`, call
`embed_and_store` from `cherenkov.ai.lattice_bridge`. **Must be
non-blocking** — LATTICE failure must never fail a scan. Start Qdrant
first: `docker start qdrant`.

Branch: `feat/wire-lattice-to-scan`. Open PR.

---

## 3D — Red Team + SecOps stubs

Create `packages/cherenkov/agents/red_team.py` (`RedTeamAgent`, model alias
`red-team`) and `agents/secops.py` (`SecOpsAgent`, model alias `secops`).
Stubs only — Phase 4 implements behavior. Export from
`agents/__init__.py`. Stub tests confirm instantiation.

Branch: `feat/agent-stubs-red-secops`. Open PR.

---

## 4 — GitHub issues batch

Run once via Jules (or `gh` locally) to create the 10 canonical work-queue
issues: dedup, LATTICE wire, TOKAMAK live, Architect agent, Red Team stub,
SecOps stub, CherenkovTrace signing, EGY-FIN CSF mapping, Arabic PDF report,
repo description fix. See source prompts §4 for verbatim `gh issue create`
commands. Label each `P0`/`P1`/`P2` plus `bug`/`enhancement`/`chore`.

---

## 5 — Jules session queue (sequenced)

| Session | Task | Branch |
|---|---|---|
| 1 | Dedup + LATTICE wire (one PR) | `fix/dedup-lattice` |
| 2 | TOKAMAK live | `feat/tokamak-live-execution` |
| 3 | Architect agent | `feat/architect-agent` |
| 4 | Red Team + SecOps stubs | `feat/agent-stubs-red-secops` |

**Do not start Session N+1 until Session N is merged.** Sessions 3 and 5
(dashboard FE, Antigravity) may run in parallel after Session 2 merges.

Smoke test after each merge (see verification gates in CLAUDE.md immediate
priority).

---

## 6 — Claude Code multi-file wiring session

Read `CLAUDE.md` and the four files: `api/main.py`, `core/tokamak.py`,
`ai/lattice_bridge.py`, `agents/` (if it exists). Then:

1. Review the scan pipeline end-to-end. Report broken imports / missing
   modules before changing anything.
2. Wire CherenkovTrace signing into scan completion (SHA-256 of result JSON,
   stored in `cherenkov_traces`, returned in response).
3. Verify Foundation-Sec via LiteLLM (curl the `architect` model).
4. Create the agent package skeleton if missing.

Branch: `feat/architect-wiring`. One PR per logical change.

---

## 7 — Open WebUI system preset

Save as a preset in Open WebUI for daily use:

```
You are the principal architect and senior engineer of CHERENKOV — a
sovereign AI security platform for MENA financial institutions.

CORE RULES:
- Package path: packages/cherenkov/ (NEVER src/)
- Imports: from cherenkov.X import Y
- Zero cloud egress enforced by MEISSNER
- ABLATION sanitizes before any external LLM call
- TOKAMAK required to confirm HIGH/CRITICAL findings
- freetsa.org for RFC 3161 timestamps (never AWS/GCP)
- Never commit to main — always branch → PR

ARCHITECTURE TIERS:
Tier 1: Core (scanners, TOKAMAK, LATTICE, ABLATION)
Tier 2: Dual-brain (TENSOR cloud-sanitized + KINETIC local Ollama)
Tier 3: Agents (Architect=Foundation-Sec, RedTeam=WhiteRabbitNeo, SecOps=Trendyol)

MODEL ROUTING via LiteLLM at localhost:4000:
  architect  → Foundation-Sec-8B-Reasoning
  red-team   → RedSage-DPO / WhiteRabbitNeo
  code-smart → qwen2.5-coder:7b
  embed      → nomic-embed-text

CURRENT PRIORITY:
1. Deduplicate scan findings
2. Wire LATTICE to scan output
3. Implement TOKAMAK live PoC execution
4. Build Architect agent layer
5. EGY-FIN CSF mapping for Cairo pilot

When asked about code, read the file before answering.
When asked about architecture, reference the three tiers.
When asked about next steps, prioritize by Cairo pilot readiness.
```

---

## Maintenance

- This file is the SSOT. If a prompt drifts in an agent session, update it
  here, not in the agent.
- New prompt? Add a section with a clear ID. Reference from CLAUDE.md /
  AGENTS.md as needed.
- Update model aliases here whenever LiteLLM config changes (Foundation-Sec
  upgrade, new red-team model, etc.).
