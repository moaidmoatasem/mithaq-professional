# CI/CD Pipeline

> *The automated quality and deployment pipeline for CHERENKOV.*

```mermaid
flowchart LR
    subgraph PR["Pull Request"]
        A[Code Change]
        B[Docs Change]
    end

    subgraph Validation["Validation Pipeline"]
        C[Ruff Format]
        D[Ruff Lint]
        E[Bandit Security]
        F[Pytest Unit]
        G[Doc Gate]
        H[MkDocs Build]
    end

    subgraph Approval["Human Review"]
        I[HITL Review]
        J[Crypto Approval]
    end

    subgraph Deploy["Deployment"]
        K[Docker Build]
        L[MkDocs Deploy]
        M[Release Tag]
    end

    A --> C
    A --> D
    A --> E
    A --> F
    B --> G
    B --> H

    C --> I
    D --> I
    E --> I
    F --> I
    G --> I
    H --> I

    I --> J
    J --> K
    J --> L
    J --> M

    K --> N["GitHub Container Registry"]
    L --> O["Cloudflare Workers\n(docs.cherenkov-security.com)"]
    M --> P["GitHub Release"]
```

## Pipeline Stages

| Stage | Tool / Action | Gate | Failure Behaviour |
|---|---|---|---|
| Format | ruff format --check | ✅ Must pass | PR blocked |
| Lint | ruff check | ✅ Must pass | PR blocked |
| Security | bandit -ll | ✅ Must pass | PR blocked |
| Unit Tests | pytest | ✅ Must pass | PR blocked |
| Doc Gate | dev_crew/doc_gate.py | ✅ Must pass | PR blocked |
| Doc Build | mkdocs build --strict | ✅ Must pass | PR blocked |
| HITL Review | Human approval | ✅ Required for core changes | PR blocked |
| Docker Build | docker buildx | ⚠️ Warning only | Notify maintainer |
| Deploy | wrangler deploy | ✅ After merge | Auto-rollback |

## What Triggers What

| Trigger | Action |
|---|---|
| Push to `docs/368-*` | Validation pipeline only |
| PR opened against `main` | Validation pipeline + HITL (if core) |
| Push to `main` | Full deploy: Docker + MkDocs + Release |
| Comment `/deploy` on PR | Manual deploy trigger (maintainer only) |