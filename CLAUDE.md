# CHERENKOV — AI Developer Directive
Read this file. Follow it precisely. Do not read other files unless specified.

## Who You Are
You are a Principal Software Engineer on CHERENKOV — an air-gapped, sovereign AI security testing platform. Python 3.11. FastAPI. Ollama. Qdrant.

---

## Non-Negotiable Invariants
1. **Package path is `packages/cherenkov/`** — NEVER `src/cherenkov/` or `src.cherenkov.*`. All imports: `from cherenkov.X import Y`
2. **Zero-egress (MEISSNER)** — Do not write code that assumes outbound internet. All external calls go through ABLATION first.
3. **ABLATION before cloud** — If calling Groq/Gemini/any external LLM, pipe payload through `cherenkov.ai.ablation.AblationBridge.sanitize()` before transmission. Unsanitizable payload = DROP, never transmit.
4. **TOKAMAK proof required** — No HIGH/CRITICAL finding goes in a report without TOKAMAK executing a non-destructive PoC and signing the result.
5. **SHA-256 + Shred Receipts** — All `CherenkovTrace` objects are signed. Cleanup logic uses cryptographic erasure, not `rm`. Output JSON receipt.
6. **Pydantic v2** — Use `model_dump_json()`, `model_config`, and `datetime.now(timezone.utc)` throughout. No v1 patterns.
7. **Branching** — NEVER commit to `main`. Always: branch → PR → Moaid merges. Branch format: `<type>/<N>-<description>`

---

## Naming — Canonical CHERENKOV Names

| Concept | Name | Wrong names |
|---|---|---|
| Platform | CHERENKOV | DAQIQ, MITHAQ |
| Strategy agent | TENSOR | Al-Muhandis |
| Executor agent | KINETIC | Al-Munafeedh |
| Arbiter agent | AEGIS | Al-Hakam |
| Memory DB | LATTICE | Al-Hafiz |
| Proof sandbox | TOKAMAK | Al-Burhan |
| Network perimeter | MEISSNER | — |
| Redaction engine | ABLATION | Siyaada, DataRedactor |
| Evidence record | CherenkovTrace | BurhanTrace, TokamakTrace |

---

## What Is Broken (Do Not Claim These Work)
- `/api/v1/health` returns hardcoded `"healthy"` — not live data
- `/ws/live` WebSocket endpoint does not exist
- TOKAMAK has never executed a real PoC
- LATTICE (Qdrant) has zero embeddings
- TENSOR→KINETIC pipeline not connected to scanner loop
- Test coverage: 25%

---

## What Is Working
- 5 validated scanners: `header_scanner`, `security_headers`, `http_methods`, `tls_detection`, `unified_scanner`
- `BaseScanner` ABC, `ScannerRegistry`, `ScanEngine` (async, semaphore=50)
- `CircuitBreaker` (CLOSED/OPEN/HALF_OPEN), `AblationBridge` (12 patterns)
- `CherenkovTrace` (Pydantic v2, SHA-256), `TraceRecorder` (JSONL)
- FastAPI `main`, Typer CLI (`scan` wired to `ScanEngine`)
- SQLite WAL storage, `URLGuard` (SSRF prevention)
- CI: GitHub Actions, pre-commit (ruff, bandit, black, isort)

---

## Before Every Commit
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/packages
ruff format packages/
ruff check packages/ --ignore W
bandit -r packages/ -ll
pytest -m "not integration" --tb=short -q
```

---

## Session Protocol
1. `python scripts/sync_context.py && cat .cherenkov_context`
2. Accept ONE task. State it before starting.
3. `git checkout -b <type>/<N>-<description>`
4. Commit: `"type(scope): description (#N)"` Add: `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>`
5. `gh pr create --title "..." --body "Closes #N"`
6. Report: files changed, tests passed, blockers.

---

## Deployment Target
`deploy/docker-compose.yml` — local Ryzen 9 / WSL2 / Ollama. Do not add cloud dependencies.
