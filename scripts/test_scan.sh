#!/bin/bash
curl -X POST http://localhost:8000/api/scan -H 'Content-Type: application/json' -d '{"target": "https://example.com", "scan_types": ["ai-agent"]}'
