# Data Tiers

CHERENKOV classifies all data into strict access tiers. Each agent node can only access data at or below its authorized level.

| Tier | Description | Examples | Accessible By |
|---|---|---|---|
| **T0 — Public** | Non-sensitive, non-identifying | CVE IDs, public domain info | All agents |
| **T1 — Internal** | Project-level metadata | Package names, dependency lists | TENSOR (after ABLATION) |
| **T2 — Sensitive** | Obfuscated findings | Sanitized breadcrumbs, hashed paths | AEGIS, TENSOR |
| **T3 — Restricted** | Raw findings | Full scan results, PII | KINETIC (local only) |
| **T4 — Quarantined** | Live exploit data | TOKAMAK sandbox state | TOKAMAK only |

Data is automatically downgraded through the pipeline. T3 data never reaches cloud agents.
