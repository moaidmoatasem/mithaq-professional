# Session Protocol

CHERENKOV agents communicate via an encrypted session protocol that enforces data access tiers and provides end-to-end integrity.

## Protocol Layers

| Layer | Purpose |
|---|---|
| **Transport** | TLS 1.3 encrypted HTTP REST connections |
| **Authentication** | Mutual mTLS with per-agent certificates |
| **Rate Limiting** | AIMD-based per-agent rate control |
| **Session** | Ephemeral session IDs with HMAC-signed payloads |

## Data Tiers

Each message is annotated with its data tier. Agents without sufficient authorization cannot read the payload.

| Tier | Description | Accessible By |
|---|---|---|
| **T2 — Sensitive** | Sanitized breadcrumbs | TENSOR, AEGIS |
| **T3 — Restricted** | Raw findings | KINETIC (local only) |
| **T4 — Quarantined** | Live exploit data | TOKAMAK only |

## BurhanTrace (Evidence Schema)

Every operation concludes with a signed trace:

```python
class BurhanTrace(BaseModel):
    timestamp: datetime
    finding_id: str
    poc_binary: bytes    # Retained only locally
    execution_log: str
    signature: str        # SHA-256(poc_binary + execution_log)
```

For detailed agent communication patterns, see [System Design & State Machine](../architecture/system-design.md).
