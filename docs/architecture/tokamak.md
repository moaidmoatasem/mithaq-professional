# TOKAMAK (The Proof)

TOKAMAK is the validation sandbox. No HIGH or CRITICAL finding is reported without TOKAMAK executing a live, non-destructive Proof of Concept (PoC) against the target.

## How It Works

| Step | Description |
|---|---|
| **Receive** | KINETIC submits a suspected vulnerability |
| **Isolate** | TOKAMAK creates an ephemeral sandbox |
| **Execute** | Runs the PoC in a contained environment |
| **Verify** | Confirms exploit success or rejects false positive |
| **Sign** | Cryptographically signs the verified finding |

## Properties

- Non-destructive — PoCs cannot modify persistent state
- Ephemeral — Sandbox is destroyed after execution
- Verified — Every finding includes cryptographic proof
