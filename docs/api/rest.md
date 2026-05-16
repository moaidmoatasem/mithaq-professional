# REST Endpoints

## Authentication

All requests require an API key in the `X-API-Key` header.

## Endpoints

### POST /api/v1/scan

Submit a new scan target.

```json
{
  "target": "https://example.com",
  "strategy": "adaptive",
  "profile": "hybrid"
}
```

**Response:** `202 Accepted`

```json
{
  "scan_id": "c7f3a2b1-...",
  "status": "queued",
  "estimated_duration": 120
}
```

### GET /api/v1/scan/{scan_id}

Retrieve scan status and results.

**Response:** `200 OK`

```json
{
  "scan_id": "c7f3a2b1-...",
  "status": "completed",
  "findings": [...],
  "trace_id": "sha256:..."
}
```

### GET /api/v1/scanners

List all registered scanners.

### GET /api/v1/compliance

Get compliance mapping for findings.
