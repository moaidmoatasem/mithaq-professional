# CLI Reference

The `cherenkov` CLI is the primary interface for interacting with the platform.

## Usage

```bash
cherenkov [command] [options]
```

## Commands

| Command | Description |
|---|---|
| `scan` | Run a security scan against a target |
| `profile` | Manage deployment profiles |
| `config` | View or validate configuration |
| `scanners` | List registered scanners |
| `traces` | View scan history and traces |
| `serve` | Start the API server and dashboard |

## Examples

```bash
# Run a scan
cherenkov scan https://example.com --output table

# List scanners
cherenkov scanners list

# Start the API server
cherenkov serve --port 8000

# View last 10 traces
cherenkov traces --limit 10
```

## Global Options

| Flag | Description |
|---|---|
| `--config PATH` | Path to config file |
| `--profile NAME` | Deployment profile |
| `--verbose` | Enable verbose logging |
| `--json` | Output in JSON format |
