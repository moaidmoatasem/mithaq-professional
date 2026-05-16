# Project briefing (single entry)

This document is the **canonical onboarding and navigation hub** for roadmap, execution plans, architecture, progress framing, curated technical debt, and major risks. It does **not** replace long-form specs; it links to them.

---

## At a glance

CHERENKOV is scoped as an air-gapped, sovereign security intelligence stack organized around three boundaries:

| Boundary | Role |
|----------|------|
| **MEISSNER** | Fail-closed network perimeter (zero egress). |
| **ABLATION** | Redaction / sanitization when data crosses trust boundaries. |
| **TOKAMAK** | Isolated validation and cryptographically attributable evidence for findings. |

**Read next:** [Product roadmap](pm/ROADMAP.md) for release phases and goals, then [System architecture](architecture/SYSTEM_ARCHITECTURE.md) for cognitive routing and the Trident model.

---

## Document hub

| Layer | Purpose | Primary documents |
|-------|---------|---------------------|
| **TPM / roadmap** | Strategy, phases, milestones | [pm/ROADMAP.md](pm/ROADMAP.md), [pm/ROADMAP_FOR_WEB.md](pm/ROADMAP_FOR_WEB.md), [github/RELEASES.md](github/RELEASES.md) |
| **Execution plans** | Sprints and deep phased plan | [pm/DEVELOPMENT_PLAN.md](pm/DEVELOPMENT_PLAN.md), [plan/development_plan.md](plan/development_plan.md) |
| **Progress timeline** | Gantt-style phased view | [plan/ROADMAP_PROGRESS.md](plan/ROADMAP_PROGRESS.md) |
| **Architecture** | System design and diagrams | [architecture/SYSTEM_ARCHITECTURE.md](architecture/SYSTEM_ARCHITECTURE.md), [architecture/HLD_DIAGRAM.md](architecture/HLD_DIAGRAM.md), [architecture/LLD_DIAGRAM.md](architecture/LLD_DIAGRAM.md) |
| **System design & patterns** | HLD/LLD narrative, patterns | [pm/SYSTEM_DESIGN.md](pm/SYSTEM_DESIGN.md), [pm/DESIGN_PATTERNS_BEST_PRACTICES.md](pm/DESIGN_PATTERNS_BEST_PRACTICES.md) |
| **Processes** | Engineering workflow | [processes/DEVELOPMENT_WORKFLOW.md](processes/DEVELOPMENT_WORKFLOW.md) |
| **Living backlog / status** | Checklists and headline status | [development/roadmap.md](development/roadmap.md) |
| **Governance / PM rules** | Branches, milestones, labels | Refer to AGENTS.md in repo root |
| **Product / narrative SSOT** | Sovereign framing | [architecture/index.md](architecture/index.md), [what-is-cherenkov.md](what-is-cherenkov.md) |
| **Risk exercise** | Prospective failure modes | See challenges and risks below |
| **Published site** | Reader-facing docs (may trail repo) | [docs.cherenkov-security.com](https://docs.cherenkov-security.com/) |

```mermaid
flowchart LR
  Briefing[project_briefing]
  Roadmap[pm_ROADMAP]
  DevPlan[pm_DEVELOPMENT_PLAN]
  DeepPlan[plan_development_plan]
  Arch[architecture_SYSTEM_ARCHITECTURE]
  Premortem[CHERENKOV_PREMORTEM]
  Briefing --> Roadmap
  Briefing --> DevPlan
  Briefing --> DeepPlan
  Briefing --> Arch
  Briefing --> Premortem
```

---

## Progress

### Timeline (from roadmap progress doc)

Synced with [plan/ROADMAP_PROGRESS.md](plan/ROADMAP_PROGRESS.md).

```mermaid
gantt
    title CHERENKOV Development Roadmap
    dateFormat  YYYY-MM-DD
    section Phase0_Week1
    Foundation_and_Pydantic_Schemas :done, p0, 2026-04-26, 7d
    Ablation_Sanitizer_and_HMAC :active, p0_2, 2026-04-28, 5d
    section Phase1_Week2_to_8
    MultiProvider_Orchestration :p1, 2026-05-03, 49d
    section Phase2_Week9_to_20
    Tool_Integration_APKTool_Frida :p2, 2026-06-21, 84d
    section Phase3_Week21_to_28
    Tokamak_Validation_Sandbox :p3, 2026-09-13, 56d
    section Phase4_Week29_to_35
    Security_Hardening_and_SBOM :p4, 2026-11-08, 49d
    section Phase5_Week36_to_41
    Enterprise_Readiness_and_UI :p5, 2026-12-27, 42d
```

That document’s status overview: **Phase 0 in progress**; **Phases 1–5 planned**.

### How to reconcile status

Multiple artifacts track “where we are.” They emphasize different lenses; **CI results, merged code, and GitHub issues** should win when they disagree with prose.

| Source | What it measures |
|--------|------------------|
| [plan/ROADMAP_PROGRESS.md](plan/ROADMAP_PROGRESS.md) | Calendar-style phases (Week 1–41 style). |
| [pm/ROADMAP.md](pm/ROADMAP.md) | Product phases aligned to releases **v1.0.0-rc1** through **v2.5.0**. |
| [development/roadmap.md](development/roadmap.md) | Product phases aligned to releases **v1.0.0-rc1** through **v2.5.0**. |
| [plan/ROADMAP_PROGRESS.md](plan/ROADMAP_PROGRESS.md) | Calendar-style gantt chart. |

If status sources diverge, treat that as a signal to **update** in a dedicated docs pass—not as contradictory truth.

---

## Technical debt (curated)

These items are **signals for triage**, not an exhaustive audit. Verify in code before prioritizing fixes.

| Theme | Notes | Evidence |
|-------|--------|----------|
| **Vision vs codebase gap** | Historical deep review listed few validated scanners vs many generated candidates, scaffold AI integration, persistence gaps, and repo layout debt. | [plan/development_plan.md](plan/development_plan.md) §2 — *dated snapshot; re-validate.* |
| **Low coverage bar** | CI allows reporting with `fail_under = 25`. | See `pyproject.toml` in repo root |
| **Stub / TODO clusters** | Orchestration iterations and dev-crew scaffolding not fully wired. | See repo source tree |
| **Web entrypoint drift** | Multiple `cherenkov_web` entrypoints exist. | See repo source tree |
| **Governance vs implementation** | Policy and architecture docs may outpace enforced controls in code (see risks). | See architecture docs |

---

## Challenges and risks (short list)

From [pm/ROADMAP.md](pm/ROADMAP.md): delivering **parallel swarm orchestration**, **enterprise HITL/compliance**, **mobile exploitation stack**, and **ecosystem export (SARIF, CI)** while preserving **zero-egress** assurances—each phase increases operational and assurance burden.

From the premortem analysis (representative prevention themes):

| Failure mode | Preventive theme |
|--------------|------------------|
| Planning heavy, shipping light | Enforce commit-first cadence vs new planning artifacts. |
| Ablation drops too much evidence | Telemetry, partial redaction fallback, staged real payloads. |
| Tokamak timeouts wrong for surface | Profile-aware timeouts (e.g. web vs mobile/boot). |
| Scanner candidates not validated | Automated nightly validation gates (targets + CI). |
| Credibility gap (marketing vs reality) | README and public claims track **validated** capabilities. |

See the premortem for the full retrospective table and prescriptions.

---

## Maintenance

Update this briefing when roadmap, milestone, or progress docs change materially—**at minimum** alongside a release tag or sprint close. Prefer a single small PR that adjusts links and debt bullets rather than expanding this file into duplicate long-form prose.

---

## Published documentation site

Material aimed at external readers and deployments is also published at **[https://docs.cherenkov-security.com/](https://docs.cherenkov-security.com/)**. Use this repository’s `docs/` paths for **source-of-truth engineering** artifacts; use the site for **curated, reader-facing** docs when versions differ, prefer reconciling both in the same release pass.
