# cherenkov.yaml

The main configuration file for CHERENKOV. Located in the project root or specified via `--config`.

## Structure

```yaml
scan:
  strategy: adaptive         # rapid | deep | stealth | adaptive
  max_concurrency: 5
  timeout: 300

agents:
  tensor:
    model: groq/llama-3.1-8b
    temperature: 0.2
  kinetic:
    model: ollama/llama-3.2-3b
    endpoint: http://localhost:11434

storage:
  lattice:
    type: qdrant
    path: ./data/lattice
  traces:
    type: sqlite
    path: ./data/traces.db

meissner:
  enabled: true
  whitelist:
    - github.com
    - nvd.nist.gov

ablation:
  rules:
    - pattern: "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}"
      type: email
      action: redact
```
