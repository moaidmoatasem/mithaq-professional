# Task: Issue #233 — Align GEMINI.md with AGENTS.md roster

**Branch:** `chore/233-gemini-align`
**Labels:** `priority:medium, chore, phase-2`
**Milestone:** v1.1.0
**PR must contain:** `Closes #233`

## Context

`GEMINI.md` is out of date — it does not reflect new agents added to the roster
(architect.py, red_team.py, secops.py, decision_hub.py). It should match `AGENTS.md`
so that Gemini-powered agents have correct context about the full agent ecosystem.

## Context files

```
AGENTS.md    ← source of truth for agent roster
GEMINI.md    ← Gemini-specific config — needs updating
```

## What to do

1. **Read current AGENTS.md** — note the Agent Roster & Domain Ownership table

2. **Update GEMINI.md**:
   - Add a "Full Agent Roster" section or table matching `AGENTS.md`
   - Add references to new agents:
     - **Security Architect** (`packages/cherenkov/orchestration/architect.py`)
     - **Red Team Agent** (`packages/cherenkov/orchestration/red_team.py`)
     - **SecOps Agent** (`packages/cherenkov/orchestration/secops.py`)
     - **Decision Hub** (`packages/cherenkov/orchestration/decision_hub.py`)
   - Update "Key GitHub Issues" table to reference current open issues (#230–#247)
   - Ensure the environment section matches current Python/Node versions

3. **Cross-check** that both files agree on:
   - Branch naming conventions
   - Commit message format
   - Pre-commit commands
   - Invariants (MEISSNER, ABLATION, TOKAMAK, Shred)

## Files to modify

- `GEMINI.md`

## Verify

```bash
# Visual diff to confirm alignment
diff <(grep -i "agent\|roster\|branch\|invariant" AGENTS.md) <(grep -i "agent\|roster\|branch\|invariant" GEMINI.md)

# No broken references
grep -n "issue-[0-9]" GEMINI.md  # should reference #230+ issues
```
