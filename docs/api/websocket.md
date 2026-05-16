# WebSocket Events

CHERENKOV provides real-time updates via WebSocket connections.

## Connection

```
ws://host:8000/api/v1/ws?token=<api_key>
```

## Events

| Event | Direction | Description |
|---|---|---|
| `scan.progress` | Server → Client | Scan progress percentage |
| `scan.finding` | Server → Client | New finding discovered |
| `scan.complete` | Server → Client | Scan finished |
| `agent.status` | Server → Client | Agent node status change |
| `gate.result` | Server → Client | Validation Gate result |

## Example

```json
{
  "event": "scan.finding",
  "data": {
    "severity": "HIGH",
    "scanner": "sqli-detector",
    "title": "SQL Injection in /login"
  }
}
```
