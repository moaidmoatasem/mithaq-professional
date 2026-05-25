# High-Level Design (HLD)

The following diagram provides a high-level view of the CHERENKOV system architecture.

```mermaid
graph TD
    Client[Web/CLI Client] --> Orchestrator[Orchestration API]
    Orchestrator --> AgentGovernor[Agent Governor\nCognitive Routing]
    AgentGovernor --> TENSOR[TENSOR\nStrategist\nOllama Qwen2.5-Coder 7B]
    AgentGovernor --> KINETIC[KINETIC\nLocal Executor\nOllama Qwen2.5-Coder 1.5B]
    AgentGovernor --> TOKAMAK[TOKAMAK\nValidator\nDocker Sandbox]
    AgentGovernor --> AEGIS[AEGIS\nArbiter & Circuit Breaker\nLocal Model]
    AgentGovernor --> LATTICE[LATTICE\nMemory & RAG\nQdrant + nomic-embed-text]

    TENSOR --> Sanitizer[ABLATION Sanitizer]
    KINETIC --> LocalEnv[Local Execution Env]
    TOKAMAK --> Sandbox[TOKAMAK Sandbox]
    LATTICE --> VectorStore[(Qdrant Vector DB)]

    style TENSOR fill:#2F5F8A,color:#fff
    style KINETIC fill:#2F5F8A,color:#fff
    style TOKAMAK fill:#9D00FF,color:#fff
    style AEGIS fill:#0A0E1A,color:#fff
    style LATTICE fill:#00A3FF,color:#fff
    style Sanitizer fill:#00E0FF,color:#000
```
