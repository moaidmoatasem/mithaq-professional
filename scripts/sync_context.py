#!/usr/bin/env python3
# scripts/sync_context.py
"""
Regenerates .cherenkov_context from ACTUAL repo state before every Claude session.
Never hardcodes anything. Truth only.

Usage:
    python scripts/sync_context.py          # update .cherenkov_context
    python scripts/sync_context.py --show   # print to stdout without writing

Run this BEFORE starting any Claude Code or Claude.ai session.
Tell Claude: "Read .cherenkov_context only. Do not ls or glob the repo."
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run(cmd: str, fallback: str = "") -> str:
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        return result.stdout.strip() or fallback
    except Exception:
        return fallback


def generate() -> str:
    lines = []
    w = lines.append

    w(f"# cherenkov CONTEXT — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    w("# Auto-generated. Do not edit manually.")
    w("")

    # ── Git state ──────────────────────────────────────────────────────────
    w("## GIT")
    branch = run("git branch --show-current", "unknown")
    w(f"Branch: {branch}")
    w("Recent commits:")
    for line in run("git log --oneline -5").splitlines():
        w(f"  {line}")
    dirty = run("git status --short | wc -l", "0").strip()
    w(f"Uncommitted changes: {dirty} files")

    # ── Security checks ────────────────────────────────────────────────────
    w("")
    w("## SECURITY STATUS")
    # Exclude tool/template files that contain these strings as text, not live code
    _excl = "grep -v '#' | grep -v 'session_manager' | grep -v 'sync_context' | grep -v 'swarm_orchestrator'"
    debug = run(f"grep -r 'debug=True' . --include='*.py' | {_excl} | wc -l", "0")
    cors = run(f"grep -r 'allow_origins=\\[\"\\*\"\\]' . --include='*.py' | {_excl} | wc -l", "0")
    bind = run(f"grep -r 'host=.0\\.0\\.0\\.0.' . --include='*.py' | {_excl} | wc -l", "0")
    nested = "EXISTS" if Path("src/cherenkov/cherenkov").exists() else "CLEAN"
    tag = run("git tag | grep security || echo NONE")
    w(f"debug=True instances: {debug} (must be 0)")
    w(f"CORS wildcard instances: {cors} (must be 0)")
    w(f"0.0.0.0 bindings: {bind} (must be 0)")
    w(f"Nested src/cherenkov/cherenkov/: {nested} (must be CLEAN)")
    w(f"Security tag: {tag}")

    # ── Source structure ───────────────────────────────────────────────────
    w("")
    w("## SOURCE")
    scanners_dir = Path("src/cherenkov/scanners")
    candidates_dir = Path("candidates/generated_scanners")
    validated = (
        sorted(p.name for p in scanners_dir.glob("*.py") if not p.name.startswith("__"))
        if scanners_dir.exists()
        else []
    )
    candidates = list(candidates_dir.glob("*.py")) if candidates_dir.exists() else []
    w(f"Validated scanners: {len(validated)}")
    for s in validated[:10]:
        w(f"  ✓ {s}")
    if len(validated) > 10:
        w(f"  ... and {len(validated)-10} more")
    w(f"Candidates (unvalidated): {len(candidates)}")

    # ── Core files existence ───────────────────────────────────────────────
    w("")
    w("## CORE FILES")
    files = {
        "BaseScanner": "src/cherenkov/core/base_scanner.py",
        "Registry": "src/cherenkov/core/registry.py",
        "Engine": "src/cherenkov/core/engine.py",
        "Ablation": "src/cherenkov/ai/ablation.py",
        "Tokamak": "src/cherenkov/agents/tokamak.py",
        "TOKAMAK": "src/cherenkov/core/tokamak.py",
        "ModelRouter": "src/cherenkov/ai/model_router.py",
        "CLI": "src/cherenkov/cli.py",
        "FastAPI": "src/cherenkov/api/main.py",
        "SQLite": "src/cherenkov/storage/database.py",
        "ScannerGen": "src/cherenkov/dev_crew/scanner_generator.py",
    }
    for name, path in files.items():
        exists = "✓" if Path(path).exists() else "✗ MISSING"
        w(f"  {name:<15} {exists}")

    # ── Test coverage ──────────────────────────────────────────────────────
    w("")
    w("## TESTS")
    test_count = run("pytest tests/ --co -q 2>/dev/null | grep 'test session' | head -1", "unknown")
    coverage = run("coverage report --include='src/*' 2>/dev/null | tail -1", "no data")
    w(f"Test count: {test_count}")
    w(f"Coverage:   {coverage}")

    # ── Current phase ──────────────────────────────────────────────────────
    w("")
    w("## PHASE STATUS")
    # Auto-detect phase from what exists
    phase = "0 (security fixes)"
    if Path("src/cherenkov/core/base_scanner.py").exists():
        phase = "2 (architecture)"
    if len(validated) >= 10:
        phase = "3 (scanner library)"
    if Path("src/cherenkov/agents/tokamak.py").exists() and len(validated) >= 20:
        phase = "4 (mobile + Tokamak)"
    w(f"Detected phase: {phase}")

    # ── Active blockers ────────────────────────────────────────────────────
    w("")
    w("## BLOCKERS (from git issues)")
    issues = run(
        r"gh issue list --state open --limit 10 --json number,title "
        r"--jq '.[] | \"  #\(.number) \(.title)\"' 2>/dev/null",
        "  gh CLI not configured or no open issues",
    )
    w(issues or "  none")

    # ── Next action ────────────────────────────────────────────────────────
    w("")
    w("## NEXT ACTION")
    if nested == "EXISTS":
        w(
            "→ Delete src/cherenkov/cherenkov/ (run: python tools/session_manager.py show fix_nested_dir)"
        )
    elif int(debug) > 0:
        w("→ Fix debug=True instances before anything else")
    elif int(cors) > 0:
        w("→ Fix CORS wildcard in api/main.py")
    elif tag == "NONE":
        w("→ Tag v0.1.1-security after all security fixes pass")
    elif not Path("src/cherenkov/core/base_scanner.py").exists():
        w("→ Create BaseScanner (run: python tools/session_manager.py show create_base_scanner)")
    elif len(validated) < 50:
        w(
            f"→ Graduate scanner candidates ({len(candidates)} pending, "
            f"run: python tools/session_manager.py show validate_candidate)"
        )
    else:
        w("→ Phase 3 complete. Start Phase 4 (mobile surface).")

    w("")
    w("## INSTRUCTIONS FOR CLAUDE CODE")
    w("Read this file only. Do not run ls -R or glob the repo.")
    w("Do not re-read files I haven't asked you to read.")
    w("Execute one task per session. Report results. Stop.")

    return "\n".join(lines)


def main():
    content = generate()
    if "--show" in sys.argv:
        print(content)
        return
    output = Path(".cherenkov_context")
    output.write_text(content, encoding="utf-8")
    lines = content.count("\n")
    print(f"[OK] .cherenkov_context updated ({lines} lines)")
    print("   Feed this to Claude before every session to save 60-80% tokens.")
    print("   Tell Claude: 'Read .cherenkov_context only.'")


if __name__ == "__main__":
    main()
