# CLAUDE.md — DAQIQ v4.1 (COMPRESSED)
# Rule: This file must stay under 120 lines. Prune ruthlessly on every update.
# Claude Code reads this every session. Every token here costs money.

## STATE
Phase: 1 (cleanup) | Version: v0.1.1 | Coverage: ~30%
Canonical source: src/daqiq/ ONLY

## BROKEN RIGHT NOW — FIX FIRST, IN ORDER
1. git config core.autocrlf input && git rm --cached -r . && git reset --hard HEAD
2. rm -rf src/daqiq/daqiq/ && git commit -m "fix: nested daqiq/daqiq/"
3. git log --oneline --all | grep -E "fd731b6|dd9a8be|93eee97" → cherry-pick all three
4. api/main.py: allow_origins=["http://localhost:5000"] AND host=os.getenv("UVICORN_HOST","127.0.0.1")
5. rm -f DAQIQ_DEVELOPMENT_PLAN.md STRATEGIC_ROADMAP.md src/DAQIQ_MASTER_PLAN.md docs/roadmap/PRODUCT_ROADMAP.md
6. git tag -a v0.1.1-security -m "Phase 0 done" && git push origin main --tags

## INVARIANTS (never violate)
- BaseScanner contract for every scanner
- Siyaada: fail-closed, telemetry on every drop, alert if drop_rate > 20%
- Raw data (Tier 1): never leaves local hardware
- Burhan: CONFIRMED/PROBABLE/UNVERIFIED/DISCARDED (not binary pass/fail)
- Sandbox: STANDARD profile (web) or MOBILE profile (APK/Frida) — two profiles only
- Watchdog: kill Burhan containers after 30s — prevents OOM

## DATA TIERS (from GOV-01)
Tier 1 (RAW): Terminal output, HTTP responses, decompiled code → local only, shred after 72h
Tier 2 (SANITIZED): Post-Siyaada → cloud-safe, structural metadata only
Tier 3 (TRACE): SHA-256 signed SQLite ledger → 7yr retention, CBE-distributable

## VALIDATION GATE (5 steps, all required)
1. Unit positive (mocked HTTP, must find vuln)
2. Unit negative (mocked HTTP, must NOT fire)
3. DVWA integration (localhost:8080)
4. WebGoat false-positive (localhost:8090)
5. bandit + CWE docstring + ruff

## NEW FILES (copy from project outputs to these paths)
src/daqiq/ai/siyaada.py         (with SiyaadaTelemetry)
src/daqiq/agents/burhan.py      (with PoC Confidence Score + watchdog)
src/daqiq/core/sandbox.py       (STANDARD + MOBILE profiles)
src/daqiq/dev_crew/scanner_generator.py  (qwen2.5-coder:7b, $0)

## DELEGATE TO LOCAL OLLAMA (do not use Claude tokens)
- Scanner boilerplate from CWE → dev_crew/scanner_generator.py
- Test stubs → dev_crew/scanner_generator.py
- pyproject.toml/Dockerfile edits → Claude Code bash directly
- Linting fixes (ruff --fix) → run directly, no LLM needed
- Git operations → run directly

## TOKEN BUDGET
muhandis_plan=2000 | triage_chunk=4000 | burhan_poc=1500 | max_output=1000
Target: $0.009/scan std | $0.003/scan cached | $0.00 local-only

## AUTONOMY CEILING (human must approve)
CRITICAL finding approval | Siyaada PR merges | Release tags | New LLM backends

## NEVER DO
count candidates/ | update README before code | skip validation gate
add aider-chat dep | bind 0.0.0.0 | log raw findings | binary Burhan pass/fail
community launch before Phase 3 (20+ validated scanners)
