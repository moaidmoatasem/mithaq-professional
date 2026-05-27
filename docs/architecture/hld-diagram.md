# CHERENKOV — High-Level Design

> A cosy, three-lens view of the system. Each lens zooms differently on the
> **same** components, so a node named `ABLATION` in *System* is the same
> `ABLATION` you see in *Flow* and the same container you see in *Deployment*.
>
> **Brand palette** — used consistently across all diagrams:
> - 🟦 `#00E0FF` — **MEISSNER** (network, sovereignty, boundaries)
> - 🟪 `#9D00FF` — **TOKAMAK** (validation, evidence, trust)
> - 🟧 `#FF7A00` — **ABLATION** (sanitisation, PII scrub)
> - ⬛ `#0A0E1A` — air-gapped substrate
> - ⚪ `#E6F1FF` — text on dark

---

## Legend & Component Map

| ID  | Name        | Role                                  | Appears in lens |
|-----|-------------|---------------------------------------|-----------------|
| `M` | MEISSNER    | Air-gapped Docker network boundary    | 1 · 2 · 3       |
| `A` | ABLATION    | PII / code-snippet scrubber           | 1 · 2 · 3       |
| `T` | TOKAMAK     | PoC validation + WAL-signed trace     | 1 · 2 · 3       |
| `G` | Governor    | Cognitive router across agents        | 1 · 2           |
| `O` | Ollama      | Local LLM inference (Ryzen 9)         | 1 · 3           |
| `Q` | Qdrant      | Vector memory (LATTICE)               | 1 · 3           |
| `S` | SQLite-WAL  | Forensic evidence store               | 1 · 2 · 3       |

Use these IDs to jump between lenses below.

---

## Lens 1 — Whole System (zoom: 🔭)

Every subsystem, one frame. Read it like a city map.

```mermaid
%%{init: {'theme':'dark','themeVariables':{
  'fontFamily':'ui-monospace, SFMono-Regular, monospace',
  'primaryColor':'#0A0E1A','primaryTextColor':'#E6F1FF',
  'lineColor':'#00E0FF','clusterBkg':'#10162A','clusterBorder':'#1F2A44'
}}}%%
flowchart TB
    subgraph EDGE["🌐 Edge — the only door in"]
        CLI[CLI / Web Client]
    end

    subgraph M["🟦 MEISSNER — air-gapped Docker network (fail-closed)"]
        direction TB
        API[Orchestration API]
        G[["G · Governor<br/>cognitive routing"]]

        subgraph AGENTS["Agent Swarm"]
            direction LR
            TENSOR[TENSOR<br/>strategist]
            KINETIC[KINETIC<br/>executor]
            AEGIS[AEGIS<br/>arbiter]
            LATTICE[LATTICE<br/>memory/RAG]
        end

        A(["🟧 A · ABLATION<br/>scrub PII + code"])
        T{{"🟪 T · TOKAMAK<br/>PoC validator"}}
        O[(O · Ollama<br/>local LLM)]
        Q[(Q · Qdrant<br/>vectors)]
        S[(S · SQLite-WAL<br/>signed traces)]
    end

    CLI -->|request| API --> G
    G --> TENSOR & KINETIC & AEGIS & LATTICE
    TENSOR -.->|outbound payload| A
    KINETIC --> O
    LATTICE --> Q
    AEGIS --> T
    T --> S

    classDef meissner fill:#0A0E1A,stroke:#00E0FF,stroke-width:2px,color:#E6F1FF
    classDef ablation fill:#1A0F05,stroke:#FF7A00,stroke-width:2px,color:#FFD9B3
    classDef tokamak  fill:#150823,stroke:#9D00FF,stroke-width:2px,color:#E9CCFF
    classDef store    fill:#0E1426,stroke:#00A3FF,stroke-width:1px,color:#CFE6FF
    class API,G,TENSOR,KINETIC,AEGIS,LATTICE meissner
    class A ablation
    class T tokamak
    class O,Q,S store
```

---

## Lens 2 — Core Flow (zoom: 🔬)

One request, end-to-end. Same nodes as Lens 1, arranged as a story.

```mermaid
%%{init: {'theme':'dark','themeVariables':{
  'fontFamily':'ui-monospace, SFMono-Regular, monospace',
  'actorBkg':'#10162A','actorBorder':'#00E0FF','actorTextColor':'#E6F1FF',
  'signalColor':'#00E0FF','signalTextColor':'#E6F1FF',
  'noteBkgColor':'#150823','noteBorderColor':'#9D00FF','noteTextColor':'#E9CCFF',
  'sequenceNumberColor':'#0A0E1A'
}}}%%
sequenceDiagram
    autonumber
    participant U as 👤 User
    participant G as G · Governor
    participant A as 🟧 A · ABLATION
    participant X as Agent (TENSOR/KINETIC)
    participant T as 🟪 T · TOKAMAK
    participant S as S · SQLite-WAL

    U->>G: prompt / scan request
    G->>A: payload (may contain PII)
    Note over A: redact secrets,<br/>strip code snippets
    A->>X: clean payload
    X-->>G: candidate finding
    G->>T: validate via local PoC
    Note over T: run in sandbox<br/>SHA-256 the result
    T->>S: append signed trace (WAL)
    S-->>U: 🧾 Cherenkov Receipt
```

---

## Lens 3 — Deployment Topology (zoom: 🛰️)

Where each box from Lens 1 actually runs. The dashed boundary is **MEISSNER**:
no arrow crosses it outbound.

```mermaid
%%{init: {'theme':'dark','themeVariables':{
  'fontFamily':'ui-monospace, SFMono-Regular, monospace',
  'primaryColor':'#0A0E1A','primaryTextColor':'#E6F1FF',
  'lineColor':'#00E0FF','clusterBkg':'#10162A','clusterBorder':'#00E0FF'
}}}%%
flowchart LR
    subgraph HOST["💻 Host — Ryzen 9 workstation"]
        direction TB
        subgraph NET["🟦 M · meissner-net (Docker bridge, no egress)"]
            direction TB
            C1["api<br/><sub>orchestrator</sub>"]
            C2["governor<br/><sub>G</sub>"]
            C3["ablation<br/><sub>🟧 A</sub>"]
            C4["tokamak<br/><sub>🟪 T · sandbox</sub>"]
            C5[("ollama<br/><sub>O · LLM</sub>")]
            C6[("qdrant<br/><sub>Q · vectors</sub>")]
            C7[("sqlite-wal<br/><sub>S · evidence</sub>")]
        end
        FS[/"./deploy<br/>shred-receipts/"/]
    end

    C1 --- C2 --- C3 --- C4
    C2 --- C5
    C2 --- C6
    C4 --- C7
    C7 -.->|cryptographic erase| FS

    classDef svc fill:#0A0E1A,stroke:#00E0FF,color:#E6F1FF
    classDef scrub fill:#1A0F05,stroke:#FF7A00,color:#FFD9B3
    classDef val fill:#150823,stroke:#9D00FF,color:#E9CCFF
    classDef store fill:#0E1426,stroke:#00A3FF,color:#CFE6FF
    class C1,C2 svc
    class C3 scrub
    class C4 val
    class C5,C6,C7 store
```

---

## How the lenses connect

```
Lens 1 (System)        Lens 2 (Flow)         Lens 3 (Deployment)
─────────────────      ──────────────        ─────────────────────
G   Governor      ◄──► step ②,⑤             container: governor
A   ABLATION      ◄──► step ③               container: ablation
T   TOKAMAK       ◄──► step ⑥               container: tokamak
S   SQLite-WAL    ◄──► step ⑦               container: sqlite-wal
M   MEISSNER      ◄──► (implicit boundary)  network: meissner-net
```

Pick the lens that matches the question you're asking:

- **"What does the system *contain*?"** → Lens 1
- **"What *happens* on a request?"** → Lens 2
- **"Where does it *run*?"** → Lens 3

All three describe the same machine.
