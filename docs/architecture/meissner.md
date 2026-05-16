# MEISSNER (The Shield)

MEISSNER is the fail-closed network perimeter. It enforces the zero-egress policy by dropping all unauthorized outbound connections, physically severing local execution nodes from the external internet.

## Key Properties

- **Fail-closed** — If MEISSNER cannot verify a connection, the connection is dropped
- **Zero-egress** — Local nodes (KINETIC, TOKAMAK) never reach the external internet
- **Configurable** — Whitelist rules for update mirrors and CVE feeds

## Enforcement

- Drops all outbound TCP/UDP except explicitly whitelisted routes
- Logs all denied connection attempts for audit
- Operates at the kernel level via iptables/nftables on Linux
