## CHERENKOV Project Rules

- Read .agents/context.md before every coding task
- Never import from src.cherenkov — always from cherenkov
- Never hardcode localhost:8000 in frontend — use API_BASE from @/src/lib/api.ts
- Run `ruff format packages/` before every Python commit
- Run `cd packages/cherenkov/web && npm run lint` before every TS commit
- Branch naming: feat/<issue>-<slug> or fix/<issue>-<slug>
- Every PR must contain "Closes #<issue>" in the body
- Never commit directly to main — branch -> PR -> Moaid merges
- Run `pytest -m "not (integration or ai_generated)" --tb=short` to verify
