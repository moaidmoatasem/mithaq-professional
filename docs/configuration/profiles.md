# Deployment Profiles

CHERENKOV supports deployment profiles for different environments.

## Available Profiles

| Profile | Description |
|---|---|
| **local** | Single-machine deployment, all agents local |
| **hybrid** | TENSOR uses cloud AI, all else local |
| **air-gapped** | Fully offline, no cloud dependencies |
| **cluster** | Multi-node deployment with distributed agents |

## Usage

```bash
cherenkov --profile hybrid scan https://example.com
```

Profiles are defined in `profiles/` directory as YAML files that override specific configuration sections.
