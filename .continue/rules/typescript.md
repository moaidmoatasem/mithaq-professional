## TypeScript/Frontend Rules

- Domain: packages/cherenkov/web/src/ only
- Vite dev on port 3000, proxies to FastAPI on port 8000
- Never hardcode localhost:8000 — use API_BASE from @/src/lib/api.ts
- Import pattern: @/src/lib/X, @/src/hooks/X, @/src/components/X
- Pre-commit: tsc --noEmit && npx vite build
- Do NOT touch packages/cherenkov/api/ or any Python files
