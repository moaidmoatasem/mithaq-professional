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
