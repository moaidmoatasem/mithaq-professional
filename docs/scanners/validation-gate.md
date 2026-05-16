# Validation Gate

The Validation Gate is the quality checkpoint between scanner output and final report. Every HIGH and CRITICAL finding must pass through TOKAMAK before it reaches the report.

## Gate Process

1. Scanner submits finding → Gate intercepts
2. Finding severity checked → HIGH/CRITICAL flagged for validation
3. TOKAMAK executes PoC in sandbox
4. **Pass** → Finding included in report, cryptographically signed
5. **Fail** → Finding downgraded or removed

## Benefits

- **Zero false positives** on HIGH/CRITICAL findings
- **Cryptographic proof** for every reported finding
- **Audit trail** — every gate decision is logged and signed
