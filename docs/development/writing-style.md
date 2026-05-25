# Writing Style Guide

> *CHERENKOV documentation must be precise, authoritative, and concise. This guide defines the standard.*

## 1. Voice & Tone

- **Voice**: Authoritative, technical, and precise. Write as an expert explaining to a capable peer.
- **Tone**: Direct and unambiguous. No marketing fluff, no hedging ("might", "could", "possibly").
- **Person**: Second-person ("you") for tutorials. Third-person for reference docs.
- **Tagline**: *"Precision in Sovereignty"* — every sentence should serve that ethos.

## 2. Heading Hierarchy

| Level | Convention | Example |
|---|---|---|
| H1 | ATX `#` — page title only | `# Data Flow` |
| H2 | ATX `##` — major section | `## Zero-Egress Guarantee` |
| H3 | ATX `###` — subsection | `### Port Map` |
| H4+ | ATX `####` — only in tables/lists | Avoid unless nested |

- Every file MUST have exactly one H1 that matches the filename-derived title.
- Do not skip levels (e.g., H1 → H3 without H2).

## 3. Admonitions

```markdown
> **Danger**: Security-critical information. Use for invariants, warnings, or irreversible actions.
> **Tip**: Best practices, optimisation advice.
> **Note**: Context, clarification, or references.
> **Warning**: Potential pitfalls, common mistakes.
```

- Use Danger for MEISSNER, ABLATION, TOKAMAK invariant violations.
- Use Tip for performance and code patterns.
- Use Note for cross-references and background context.

## 4. Code Blocks

- Always specify the language: `python`, `json`, `bash`, `mermaid`, `yaml`.
- Maximum line length: 80 characters. Wrap manually where needed.
- Console output: use `text` language tag.
- For inline code: use single backticks.

```python
# Good — typed, documented, 80-char wrapped
def validate_trace(trace_id: str) -> bool:
    """Check that a CherenkovTrace exists and is properly signed."""
    return trace_id.startswith("sha256:")
```

## 5. Links

| Source Type | Link Format | Example |
|---|---|---|
| Within `docs/` | Relative path | `[Data Flow](../architecture/data-flow.md)` |
| Root-level `.md` | Absolute from repo | `[CONTRIBUTING.md](https://github.com/moaidmoatasem/cherenkov-professional/blob/main/CONTRIBUTING.md)` |
| External URL | Full URL | `[docs.cherenkov-security.com](https://docs.cherenkov-security.com)` |
| GitHub Issues | `#NNN` | `[#368](https://github.com/moaidmoatasem/cherenkov-professional/issues/368)` |

- Never use `[text](path)` where `path` is a Windows-style path.
- All paths must resolve. Run `doc_gate.py validate` before committing.

## 6. Diagrams

- Every architecture document MUST include at least one Mermaid diagram.
- Diagram theme: `dark`. Use `#00A3FF` for primary, `#0A0E1A` for background.
- Diagram types by context:
  - **Architecture overview**: `graph TD` or `flowchart LR`
  - **Process flow**: `sequenceDiagram`
  - **State transitions**: `stateDiagram-v2`
  - **Timeline**: `gantt`
- Each diagram must have a preceding heading and a brief description.

## 7. File Naming

| Rule | Convention | Example |
|---|---|---|
| File name | `kebab-case.md` | `agent-state-machine.md` |
| Directory | `kebab-case/` | `docs/governance/` |
| Title (H1) | Title Case | `# Agent State Machine` |
| Allowed chars | `[a-z0-9-]` only | No spaces, underscores, or special chars |

## 8. Agent Signature

Every AI-generated document MUST include a frontmatter comment:

```markdown
<!-- Agent: Claude Sonnet 4.6 | Generated: 2026-05-25 | Issue: #368 -->
```

## 9. Cross-Reference Validation

All of the following are validated by `doc_gate.py`:

- [ ] All `[text](path)` links resolve to existing files
- [ ] No broken anchors (anchor checking is best-effort)
- [ ] Every architecture doc has >= 1 Mermaid diagram
- [ ] File names match manifest entries
- [ ] H1 matches expected title

## 10. Pre-Commit Checklist

Before committing documentation changes:

1. `markdownlint docs/` — fix all errors
2. `python dev_crew/doc_gate.py validate --manifest docs/manifest.json` — pass all checks
3. `mkdocs build --strict` — build succeeds with no warnings