# Error Codes

CHERENKOV uses standard HTTP status codes with structured error responses.

## Error Response Format

```json
{
  "error": {
    "code": "SCAN_NOT_FOUND",
    "message": "No scan found with the given ID",
    "details": {}
  }
}
```

## Common Errors

| Code | HTTP Status | Description |
|---|---|---|
| `SCAN_NOT_FOUND` | 404 | Scan ID does not exist |
| `INVALID_TARGET` | 400 | Target URL is malformed or unreachable |
| `RATE_LIMITED` | 429 | Too many requests |
| `UNAUTHORIZED` | 401 | Invalid or missing API key |
| `GATE_REJECTED` | 422 | Finding failed Validation Gate |
| `MEISSNER_BLOCKED` | 403 | Target or operation blocked by MEISSNER |
| `AGENT_UNAVAILABLE` | 503 | Required AI agent is offline |
