# CLAUDE.md — mithaq Memory File
# Auto-loaded by Claude Code every session.
# Updated: May 2026 — V4.1 (incorporates Gemini + Copilot + Arch reviews)

## Current state
- Phase: 1 (Foundation cleanup — in progress)
- Version: v0.1.1-security
- Plan: docs/plan/development_plan.md + mithaq_FINAL_PLAN_V4.md
- Test coverage: ~30% (target: 80% by v1.0)

## What's broken right now (fix before anything else)
1. 131 files showing as "modified" — line-ending noise (git config + reset)
2. src/mithaq/mithaq/ nested duplicate directory — delete it
3. Phase 2 commits lost at fd731b6 — cherry-pick them
4. api/main.py CORS wildcard + 0.0.0.0 binding — restrict both
5. 5 dead plan files in repo — delete them

## Architectural invariants (cannot be violated)
1. Every scanner inherits from BaseScanner
2. Siyaada bridge is fail-closed — drop on inability to sanitize
3. No raw data (credentials, source, binaries, IPs) leaves local hardware
4. HIGH/CRITICAL findings require Burhan validation before reporting
5. src/mithaq/ is the ONLY canonical source path
6. Candidates/ is NEVER counted as working scanners

## NEW: PoC Confidence Score (replaces binary pass/fail)
Accepted from Gemini + Copilot reviews:
- CONFIRMED  → PoC succeeded → SHA-256 signed Burhan stamp
- PROBABLE   → Env mismatch / timeout → human review queue, labeled in report
- UNVERIFIED → No safe primitive for this surface → labeled in report
- DISCARDED  → PoC definitively failed → removed from report
NEVER drop PROBABLE findings silently.

## NEW: Siyaada drop telemetry (first-class feature)
Accepted from all three reviews:
- Track: attempts, successes, drops, drop_reasons, duration_ms
- Expose in CLI output and SQLite
- Alert if drop_rate > 20% after 10 attempts
- This prevents fail-closed from being an invisible black box

## NEW: Two sandbox profiles
Accepted from Copilot:
- STANDARD: web/infra — strict, cap_drop ALL, seccomp enabled
- MOBILE: APK/Frida — adds SYS_PTRACE, larger RAM, separate network
  Mobile profile requires audit note in every container start log.

## NEW: Watchdog timer for Burhan agents
Accepted from Arch review:
- POC_TIMEOUT_SECONDS = 30 (kill stalled containers)
- BurhanAgent._kill_stalled_container() frees memory before next spawn
- Prevents hanging exploits from OOMing worker nodes

## Validation gate (5 steps — mandatory for every scanner)
1. Unit test: positive case (finds vuln with mocked HTTP)
2. Unit test: negative case (no false positive when vuln absent)
3. Integration test: fires on DVWA running in Docker (localhost:8080)
4. Does NOT fire on OWASP WebGoat safe pages (localhost:8090)
5. bandit clean + CWE in docstring + remediation guidance

## Token budget rules
- Use local Ollama (qwen2.5-coder:7b) for boilerplate — $0
- Provider-side caching for static prompts (cache_control)
- Pre-flight token count before dispatch
- Budgets: muhandis_plan=2000, triage_chunk=4000, burhan_poc=1500, max_output=1000
- Target: ~$0.009/scan standard, ~$0.003/scan cached, $0 local-only

## Source of truth paths
- Plan: mithaq_FINAL_PLAN_V4.md (authoritative)
- Arch: docs/ARCHITECTURE.md
- This file: CLAUDE.md (overrides plan where they differ — reality wins)

## What NOT to do
- Do NOT count candidates/ as official scanners
- Do NOT update README before the code matches
- Do NOT skip the validation gate. Ever.
- Do NOT add aider-chat as a dependency
- Do NOT bind any service to 0.0.0.0 without env var override
- Do NOT log raw findings — only sanitized finding descriptors
- Do NOT use binary pass/fail for Burhan — use PoC Confidence Score
- Do NOT let Siyaada drop silently — telemetry must record every drop
- Do NOT publish to community before Phase 3 (20+ validated scanners)
- Do NOT merge PRs touching Siyaada without human review

## Autonomy ceiling (human approval required)
- Approving CRITICAL findings (Burhan confirms, human reviews)
- Merging PRs touching Siyaada bridge
- Pushing release tags
- Adding new LLM backends
- Removing or weakening the validation gate
- Changing fail-closed to fail-open

## New files to add in Phase 2
src/mithaq/ai/siyaada.py         ← with SiyaadaTelemetry
src/mithaq/agents/burhan.py      ← with PoC Confidence Score + watchdog
src/mithaq/core/sandbox.py       ← with STANDARD + MOBILE profiles
src/mithaq/dev_crew/scanner_generator.py  ← qwen2.5-coder:7b local

