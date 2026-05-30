# Low-Level Design (LLD)

The following diagram details the interactions and components within the multi-agent swarm.

```mermaid
sequenceDiagram
    participant User
    participant Orchestrator
    participant Governor as Agent Governor
    participant Sanitizer as Ablation Sanitizer
    participant Tensor as TENSOR (Ollama Qwen 7B)
    participant Kinetic as KINETIC (Ollama Qwen 1.5B)
    participant Tokamak as TOKAMAK (Docker PoC)
    participant Lattice as LATTICE (Qdrant + nomic)

    User->>Orchestrator: Submit Scan Request
    Orchestrator->>Governor: Route Task
    Governor->>Lattice: Retrieve Context (CVEs / dialect)
    Lattice-->>Governor: Context Vectors

    alt Needs Strategic Planning
        Governor->>Sanitizer: Redact PII / code
        Sanitizer-->>Governor: Cleaned payload
        Governor->>Tensor: Request attack plan
        Tensor-->>Governor: Attack chain schema
    end

    Governor->>Kinetic: Dispatch execution task
    Kinetic->>Kinetic: Run scanners / triage
    Kinetic-->>Governor: Findings collected

    Governor->>Tokamak: Validate via PoC
    Tokamak->>Tokamak: Sandbox execution
    Tokamak-->>Governor: PoC result + trace

    Governor->>Governor: Compile CherenkovTrace
    Governor->>Orchestrator: Aggregated result
    Orchestrator-->>User: Signed report
```
