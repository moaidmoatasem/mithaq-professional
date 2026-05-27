# Deployment Topology

> *The physical and logical network boundaries of the CHERENKOV stack.*

```mermaid
graph TB
    subgraph "WSL2 / Linux Host"
        subgraph "MEISSNER Network Boundary"
            direction TB
            subgraph "Docker Compose Stack"
                Nginx[Nginx Reverse Proxy\n:80 / :443]
                API[FastAPI\n:8000]
                HUD[React HUD\n:3000]
                Qdrant[Qdrant\n:6333]
                Ollama[Ollama\n:11434]
                TOKAMAK_Sandbox[TOKAMAK Sandbox\nEphemeral]

                Nginx --> API
                API --> HUD
                API --> Qdrant
                API --> Ollama
                API --> TOKAMAK_Sandbox
            end
        end

        subgraph "Host Hardware"
            CPU[AMD Ryzen 9\n16 Cores]
            RAM[32 GB DDR5]
            GPU[NVIDIA RTX\nOptional]
        end

        Docker --> CPU
        Docker --> RAM
        Docker --> GPU
    end

    subgraph "External Network (Blocked)"
        Internet[Internet / Cloud]
    end

    User[User Browser] --> Nginx
    CLI[CLI Terminal] --> Nginx

    Nginx -.->|"BLOCKED by MEISSNER"| Internet
```

## Port Map

| Service | Internal Port | Protocol | Access |
|---|---|---|---|
| Nginx | 80, 443 | HTTP/HTTPS | Host LAN |
| FastAPI | 8000 | HTTP/WS | Internal only |
| React HUD | 3000 | HTTP | Host LAN (via Nginx) |
| Qdrant | 6333 | gRPC | Internal only |
| Ollama | 11434 | HTTP | Internal only |
| TOKAMAK Sandbox | Dynamic | Ephemeral | Internal only |

## Air-Gap Enforcement

| Vector | Enforcement | Mechanism |
|---|---|---|
| Outbound HTTP(S) | DROPPED | iptables rules + Docker network policy |
| DNS queries | DROPPED | MEISSNER DNS proxy returns NXDOMAIN for external |
| Package installs | RESTRICTED | Private registry mirror + pre-approved cache |
| LLM inference | LOCAL ONLY | Ollama on localhost, never cloud API |
| Vector DB | LOCAL ONLY | Qdrant in Docker, no external sync |