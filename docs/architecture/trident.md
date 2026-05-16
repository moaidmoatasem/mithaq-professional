# The Trident of Truth

The Trident is the foundational architectural pattern of CHERENKOV — three physical and cryptographic constraints that guarantee sovereign security testing.

## The Three Prongs

| Component | Role | Constraint |
|---|---|---|
| **MEISSNER** | Network perimeter shield | Zero-egress, drops unauthorized outbound packets |
| **ABLATION** | Data redaction engine | Strips PII, API keys, proprietary code before egress |
| **TOKAMAK** | Proof execution sandbox | Ephemeral, isolated kernel for live PoC validation |

## Data Flow

1. Target identified → MEISSNER locks down the network
2. If cloud analysis is needed → ABLATION sanitizes the data
3. Vulnerability found → TOKAMAK proves it in isolation
4. Result signed → SHA-256 cryptographic trace generated
