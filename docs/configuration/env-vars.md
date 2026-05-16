# Environment Variables

CHERENKOV reads configuration from environment variables for sensitive values and deployment-specific settings.

## Core

| Variable | Default | Description |
|---|---|---|
| `CHERENKOV_PROFILE` | `local` | Deployment profile |
| `CHERENKOV_CONFIG` | `./cherenkov.yaml` | Config file path |
| `CHERENKOV_DATA_DIR` | `./data` | Data storage root |

## Agents

| Variable | Default | Description |
|---|---|---|
| `TENSOR_API_KEY` | — | Groq API key for TENSOR |
| `TENSOR_MODEL` | `llama-3.1-8b` | TENSOR model |
| `OLLAMA_ENDPOINT` | `http://localhost:11434` | Ollama endpoint |
| `KINETIC_MODEL` | `llama-3.2-3b` | KINETIC model |

## Storage

| Variable | Default | Description |
|---|---|---|
| `LATTICE_PATH` | `./data/lattice` | Qdrant storage path |
| `LATTICE_PORT` | `6333` | Qdrant port |
| `TRACES_DB_PATH` | `./data/traces.db` | SQLite trace database path |
