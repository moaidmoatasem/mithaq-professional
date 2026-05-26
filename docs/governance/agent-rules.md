# Agent Rules — Sovereign Development Mandate

> *If you are an AI agent reading this, you are bound by the following rules. You do not possess architectural authority. You are an Execution Node.*

## 1. The Read-SSOT Mandate

Before writing, modifying, or deleting any core logic, you MUST read and acknowledge the canonical source of truth:

| Document | Purpose |
|---|---|
| `ARCHITECTURE.md` | Canonical layout, import convention, compliance targets |
| `CLAUDE.md` | Core architectural invariants (MEISSNER, ABLATION, TOKAMAK) |
| `AGENTS.md` | Branching, worktree, rebase, and multi-agent coordination |
| `docs/manifest.json` | Canonical doc registry — every topic mapped to its source |
| `docs/development/writing-style.md` | Voice, tone, heading hierarchy, code block rules |
| `docs/governance/code-of-conduct.md` | The Shield of Conduct — ethical and technical standards |

## 2. The Physical-Physics Axiom

All code generated must align with the Tri-Partite Engine:

- **ABLATION**: Payload sanitisation and schema redaction. No PII, credentials, or proprietary code leaves the node.
- **TOKAMAK**: Ephemeral, hardware-isolated detonation sandbox. Findings produce SHA-256 signed CherenkovTraces.
- **MEISSNER**: Zero-egress network isolation. Fail-closed hooks. No outbound internet without explicit audit.

**You do not write standard probabilistic scanning logic.** All threat validation must produce a physical CherenkovTrace.

## 3. Anti-Drift Guardrails

| Rule | Violation Consequences |
|---|---|
| No external API calls — no telemetry, logs, analytics to third-party clouds | Sovereign breach — rejected by Hub |
| No "dev-mode" or "debug" flags that bypass MEISSNER | Sovereign breach — permanent ban |
| Crypto traces only — no standard console logs for findings | Rejected by validation gate |
| Never create planning/tracking documents (TODO.md, STATUS.md clones) | Reverted — use conversation context |
| Always pipe through ABLATION before external API calls | Rejected by pre-commit hook |

## 4. Agent Documentation Compliance

When generating or modifying documentation:

1. **Structure**: Follow the Writing Style Guide (`docs/development/writing-style.md`)
2. **Cross-References**: All `[Reference](#reference)` links must resolve. Run `doc_gate.py validate` before committing.
3. **Diagrams**: Every architecture doc MUST include at least one Mermaid diagram.
4. **Manifest**: Every new doc MUST be registered in `docs/manifest.json`.
5. **Naming**: File names must be `kebab-case.md`. Titles must match H1.
6. **Signature**: Each AI-generated doc MUST declare `Agent: <name>` in a frontmatter comment.

## 5. Agent Handoff Protocol

When handing off context to another agent:

- Output complete `AgentState` including: `id`, `cognitive_load`, `active_missions`, `last_trace_id`, `circuit_breaker_status`
- Include the current branch name, issue number, and a summary of remaining work
- Attach the CherenkovTrace of your last action

---

*Violations of these rules are Sovereign Breaches and will be rejected by the validation gate.*