#!/usr/bin/env python3
# tools/session_manager.py
"""
DAQIQ Claude Code session templates.

Problem: Claude Code sessions keep hitting context limits mid-execution.
Cause:   Sessions are too broad (multiple phases in one run).
Solution: Scoped sessions with hard single-responsibility rules.

Usage:
    python tools/session_manager.py list         # show available session templates
    python tools/session_manager.py show <name>  # print prompt to paste into Claude Code
    python tools/session_manager.py next         # suggest next session based on CLAUDE.md state
"""

import sys
from textwrap import dedent

SESSIONS = {

    # ── Phase 1 cleanup — one task per session ──────────────────────────────

    "fix_line_endings": dedent("""
        SCOPE: Fix line-ending noise. ONLY this. Nothing else.

        Run:
          git config core.autocrlf input
          git rm --cached -r .
          git reset --hard HEAD
          git status

        Expected: working tree is clean. If not, report what's still modified.
        Do NOT touch any other file.
    """).strip(),

    "fix_nested_dir": dedent("""
        SCOPE: Delete nested duplicate. ONLY this.

        Run:
          ls src/daqiq/daqiq/
          rm -rf src/daqiq/daqiq/
          git add -A
          git commit -m "fix: remove nested src/daqiq/daqiq/ duplicate"
          git push origin main

        Expected: src/daqiq/daqiq/ no longer exists. Report commit hash.
    """).strip(),

    "recover_phase2": dedent("""
        SCOPE: Recover lost Phase 2 commits. ONLY this.

        Run:
          git log --oneline --all | head -30
        Find commits for: BaseScanner, Registry, Engine (around fd731b6).
        Cherry-pick them onto main. Push. Report which commits were recovered.
        Do NOT modify any other code.
    """).strip(),

    "fix_api_security": dedent("""
        SCOPE: Fix two security issues in api/main.py. ONLY these two.

        1. Replace: allow_origins=["*"]
           With:    allow_origins=["http://localhost:5000", "http://127.0.0.1:5000"]

        2. Replace: uvicorn.run(..., host="0.0.0.0", ...)
           With:    host=os.getenv("UVICORN_HOST", "127.0.0.1")
           Add:     import os at top if missing

        Commit: "fix(security): restrict CORS origins and bind API to localhost"
        Push. Report the exact lines changed.
    """).strip(),

    "delete_dead_files": dedent("""
        SCOPE: Delete 4 dead planning files. ONLY this.

        Files to delete (if they exist):
          DAQIQ_DEVELOPMENT_PLAN.md  (0 bytes placeholder)
          STRATEGIC_ROADMAP.md       (pre-Phase 0 stale)
          src/DAQIQ_MASTER_PLAN.md   (25 lines, outdated)
          docs/roadmap/PRODUCT_ROADMAP.md  (claims "$1M ARR ✅" — false)

        Do NOT delete docs/plan/development_plan.md (that is the real plan).
        Commit: "chore: remove empty and stale planning files"
        Push. Report which files were deleted.
    """).strip(),

    "tag_release": dedent("""
        SCOPE: Tag v0.1.1-security. ONLY this.

        Prerequisites (verify before tagging):
          grep -r "debug=True" . --include="*.py"  → must return nothing
          grep -r "host='0.0.0.0'" . --include="*.py"  → must return nothing
          ls src/daqiq/daqiq/ 2>/dev/null && echo EXISTS || echo CLEAN

        If prerequisites pass:
          git tag -a v0.1.1-security -m "Phase 0 security fixes complete"
          git push origin main --tags
          gh release create v0.1.1-security --title "v0.1.1 — Security patch" \\
            --notes "Fixes CVSS 10.0 RCE (Flask debug) and CVSS 9.0 XSS"

        Report: release URL.
    """).strip(),

    # ── Phase 2 — one component per session ─────────────────────────────────

    "create_base_scanner": dedent("""
        SCOPE: Create src/daqiq/core/base_scanner.py only.

        Read: the BaseScanner spec in CLAUDE.md and DAQIQ_FINAL_PLAN_V4.md section 2.2.
        Create the file with: Severity enum, Finding dataclass, ScanResult dataclass, BaseScanner ABC.
        Write tests: tests/unit/core/test_base_scanner.py (basic instantiation tests).
        Run: pytest tests/unit/core/ -v
        Commit: "feat(core): BaseScanner abstract contract"
        Push. Report coverage delta.
    """).strip(),

    "create_registry": dedent("""
        SCOPE: Create src/daqiq/core/registry.py only.

        Prerequisite: src/daqiq/core/base_scanner.py must exist.
        Read: registry auto-discovery spec in CLAUDE.md.
        Implement: load_all_scanners(), get_scanner(), all_scanners().
        Write tests: tests/unit/core/test_registry.py.
        Run: pytest tests/unit/core/test_registry.py -v
        Commit: "feat(core): scanner auto-discovery registry"
        Push.
    """).strip(),

    "create_siyaada": dedent("""
        SCOPE: Copy siyaada.py to src/daqiq/ai/siyaada.py and wire it.

        Source file is in the project outputs. Copy it verbatim — do not rewrite.
        Run: python -c "from daqiq.ai.siyaada import SiyaadaBridge; print('OK')"
        Write: tests/unit/ai/test_siyaada.py with at least 3 tests:
          - sanitize() returns SanitizationResult for safe payload
          - sanitize() raises SanitizationError for AWS key in payload
          - telemetry records both successes and drops
        Run: pytest tests/unit/ai/test_siyaada.py -v
        Commit: "feat(ai): Siyaada sanitization bridge with telemetry"
        Push.
    """).strip(),

    "validate_candidate": dedent("""
        SCOPE: Run the 5-step validation gate on ONE scanner candidate.

        Usage: Replace SCANNER_NAME with the actual file in candidates/generated_scanners/

        Steps:
          1. docker run -d -p 8080:80 --name dvwa vulnerables/web-dvwa
          2. docker run -d -p 8090:8080 --name webgoat webgoat/goat-and-wolf
          3. pytest tests/unit/scanners/test_SCANNER_NAME.py -v         (steps 1+2)
          4. pytest tests/integration/ -k SCANNER_NAME -m requires_dvwa -v   (step 3)
          5. pytest tests/integration/ -k SCANNER_NAME -m webgoat -v         (step 4)
          6. bandit -r candidates/generated_scanners/SCANNER_NAME.py -ll      (step 5)
          7. If ALL pass:
             mv candidates/generated_scanners/SCANNER_NAME.py src/daqiq/scanners/
             git add -A && git commit -m "feat(scanner): graduate SCANNER_NAME from candidates"
             gh issue close <issue-number> --comment "Validated — DVWA + WebGoat + bandit passed"

        Do NOT graduate if any step fails. Comment on the issue with what failed.
    """).strip(),

    # ── Ongoing maintenance ──────────────────────────────────────────────────

    "update_readme": dedent("""
        SCOPE: Update README.md to match current reality. ONLY this.

        Count validated scanners: ls src/daqiq/scanners/ | wc -l
        Get coverage: pytest --co -q 2>/dev/null | tail -1
        Get version: grep 'version' pyproject.toml | head -1

        Update README sections:
          - "What works today" → list ONLY src/daqiq/scanners/ contents
          - Metrics table → use actual numbers from above commands
          - Remove any claim not backed by working code

        Do NOT change architecture descriptions or the roadmap section.
        Commit: "docs: update README to reflect current state"
        Push.
    """).strip(),

    "daily_validation": dedent("""
        SCOPE: Run the autonomous nightly validation pass. This is what CI should do.

        1. docker-compose up dvwa webgoat -d 2>/dev/null || true
        2. python src/daqiq/dev_crew/scanner_generator.py --from-cve-feed --limit 3
        3. for candidate in candidates/generated_scanners/*.py; do
             daqiq-dev validate "$candidate"
           done
        4. Open PRs for any candidate that passed all 5 steps
        5. Comment on failing candidates with which step failed and why
        6. Report: X passed, Y failed, Z PRs opened
    """).strip(),
}


def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/session_manager.py [list|show <name>|next]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "list":
        print("\nAvailable session templates:\n")
        for name, prompt in SESSIONS.items():
            first_line = prompt.split("\n")[0].replace("SCOPE: ", "")
            print(f"  {name:<30} {first_line}")

    elif cmd == "show":
        if len(sys.argv) < 3:
            print("Usage: show <session_name>")
            sys.exit(1)
        name = sys.argv[2]
        if name not in SESSIONS:
            print(f"Unknown session: {name}")
            print(f"Available: {', '.join(SESSIONS.keys())}")
            sys.exit(1)
        print("\n" + "═" * 60)
        print(f"Session: {name}")
        print("═" * 60)
        print(SESSIONS[name])
        print("═" * 60)
        print("\nPaste the above into Claude Code.")

    elif cmd == "next":
        # Simple heuristic based on git status
        import subprocess
        try:
            result = subprocess.run(
                ["git", "status", "--short"], capture_output=True, text=True
            )
            if "daqiq/daqiq" in subprocess.run(
                ["find", "src/daqiq", "-name", "daqiq", "-type", "d"],
                capture_output=True, text=True
            ).stdout:
                print("Next: python tools/session_manager.py show fix_nested_dir")
            elif len(result.stdout.strip().splitlines()) > 50:
                print("Next: python tools/session_manager.py show fix_line_endings")
            else:
                print("Next: python tools/session_manager.py show fix_api_security")
        except Exception:
            print("Next: python tools/session_manager.py show fix_line_endings")

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
