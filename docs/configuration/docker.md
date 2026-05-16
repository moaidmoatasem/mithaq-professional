# Docker Compose

CHERENKOV is built for Docker-native deployment. The standard setup uses Docker Compose to orchestrate all services.

## Quick Start

```bash
docker-compose -f deploy/docker-compose.yml up -d
```

## Services

| Service | Image | Purpose |
|---|---|---|
| `orchestrator` | cherenkov/orchestrator | Main API and orchestration |
| `kinetic` | cherenkov/kinetic | Local AI executor |
| `lattice` | qdrant/qdrant | Vector memory store |
| `tokamak` | cherenkov/tokamak | Proof validation sandbox |
| `dashboard` | cherenkov/dashboard | Web UI |

## Configuration

Environment variables can be set in a `.env` file:

```env
CHERENKOV_PROFILE=hybrid
OLLAMA_ENDPOINT=http://host.docker.internal:11434
LATTICE_PATH=/data/lattice
```
