# CHERENKOV API Documentation

Welcome to the CHERENKOV API reference. The API is designed for air-gapped, zero-egress environments.

## Endpoints

### `/api/v1/health`
Returns system health, including TOKAMAK sandbox status and Ollama availability.

### `/api/v1/scan`
Initiates a new vulnerability scan.

### `/api/v1/architect/plan`
Generates a security architecture plan using Foundation-Sec-8B via the LiteLLM proxy. Input is sanitized through ABLATION.

### `/api/v1/auth/token`
Generates a short-lived JWT token for authentication.

### `/api/auth/status`
Returns the status of the authentication system, including whether a first-boot credential rotation is required.

### `/api/v1/scan/{scan_id}/compliance/{framework}/pdf`
Downloads a cryptographically signed compliance PDF report for a specific framework (e.g. `egyfincsf`, `dora`). The response includes an `X-SHA256` header corresponding to the forensic trace signature of the scan findings, and the PDF contains an RFC 3161 timestamp anchor if the TSA service is accessible.
