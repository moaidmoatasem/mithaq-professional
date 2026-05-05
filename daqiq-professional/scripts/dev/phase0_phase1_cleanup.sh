#!/usr/bin/env bash
# scripts/dev/phase0_phase1_cleanup.sh
# Run this from the root of daqiq-professional/
# It executes Phase 0 security fixes + Phase 1 cleanup automatically.
# Review each section before running. Never run blindly.

set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

echo "=== DAQIQ Phase 0 + Phase 1 Cleanup ==="
echo "Working directory: $ROOT"
echo ""

# ─────────────────────────────────────────
# PHASE 0 — Security fixes
# ─────────────────────────────────────────

echo "→ Phase 0: Patching Flask debug mode..."
# Replace the __main__ block in daqiq_web.py
python3 - << 'PYEOF'
import re, pathlib

path = pathlib.Path("daqiq_web.py")
if not path.exists():
    print("  daqiq_web.py not found — skipping")
    exit(0)

src = path.read_text()

# Replace app.run with safe version
old = r"app\.run\(debug=True.*?\)"
new = """app.run(
        debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true',
        host=os.getenv('FLASK_HOST', '127.0.0.1'),
        port=int(os.getenv('FLASK_PORT', '5000'))
    )"""
src = re.sub(old, new, src)

# Ensure os is imported
if "import os" not in src:
    src = "import os\n" + src

path.write_text(src)
print("  Flask debug mode patched.")
PYEOF

echo "→ Phase 0: Checking for remaining bare except handlers..."
COUNT=$(grep -rn "except:" . --include="*.py" | grep -v "#" | grep -v "except Exception" | wc -l || true)
if [ "$COUNT" -gt 0 ]; then
    echo "  WARNING: $COUNT bare except: found. Fix manually:"
    grep -rn "except:" . --include="*.py" | grep -v "#" | grep -v "except Exception" || true
else
    echo "  No bare excepts found."
fi

echo "→ Phase 0: Creating .env.example..."
cat > .env.example << 'ENV'
FLASK_DEBUG=false
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
DAQIQ_OLLAMA_URL=http://localhost:11434
DAQIQ_OLLAMA_MODEL=qwen2.5-coder:7b
DAQIQ_DB_URL=               # Leave blank for SQLite default
ENV
echo "  .env.example created."

# ─────────────────────────────────────────
# PHASE 1 — Repo cleanup
# ─────────────────────────────────────────

echo ""
echo "→ Phase 1: Removing development diary files..."
for f in TONIGHT_ACHIEVEMENTS.md SESSION_ACHIEVEMENTS.md AGENT_MEMORY.md \
          PROJECT_SUMMARY.md README.md.backup README_BADGES.txt; do
    if [ -f "$f" ]; then
        git rm --cached "$f" 2>/dev/null || true
        rm -f "$f"
        echo "  Removed: $f"
    fi
done

# Remove orphaned daqiq-nexus-web file (not a directory)
if [ -f "daqiq-nexus-web" ]; then
    git rm --cached "daqiq-nexus-web" 2>/dev/null || true
    rm -f "daqiq-nexus-web"
    echo "  Removed: daqiq-nexus-web"
fi

echo "→ Phase 1: Moving scanner candidates to candidates/..."
mkdir -p candidates/generated_scanners

for dir in swarm_outputs orchestration_iterations autonomous_development; do
    if [ -d "$dir" ]; then
        mv "$dir"/* candidates/generated_scanners/ 2>/dev/null || true
        rmdir "$dir" 2>/dev/null || true
        echo "  Moved $dir → candidates/generated_scanners/"
    fi
done

if [ ! -f "candidates/README.md" ]; then
cat > candidates/README.md << 'CAND'
# Scanner Candidates

AI-generated scanner drafts awaiting validation.
A scanner graduates to src/daqiq/scanners/ only after passing ALL of:

1. Unit test: positive case (finds vuln with mocked HTTP)
2. Unit test: negative case (no false positive when vuln absent)
3. Integration test: fires on DVWA or bWAPP running in Docker
4. Does NOT fire on OWASP WebGoat safe pages
5. bandit: no new security issues
6. Docstring: CWE ID, description, technique, remediation

See CONTRIBUTING.md for the full validation guide.
CAND
echo "  Created candidates/README.md"
fi

echo "→ Phase 1: Moving scripts to scripts/..."
mkdir -p scripts/dev scripts/docker

for f in launch_*.sh celebration_scan.sh deploy_now.sh dockerize_everything.sh \
          batch_scan.sh run_all_systems.sh run_autonomous_agent.sh test_scan.sh; do
    if [ -f "$f" ]; then
        mv "$f" scripts/dev/
        echo "  Moved $f → scripts/dev/"
    fi
done

for f in get-docker.sh docker-manage.sh; do
    if [ -f "$f" ]; then
        mv "$f" scripts/docker/
        echo "  Moved $f → scripts/docker/"
    fi
done

echo "→ Phase 1: Moving tools to tools/..."
mkdir -p tools
for f in analyze_generated_scanners.py extract_scanners.py refine_scanners.py \
          auto_improve_scanners.py autonomous_roadmap_executor.py; do
    if [ -f "$f" ]; then
        mv "$f" tools/
        echo "  Moved $f → tools/"
    fi
done

echo "→ Phase 1: Updating .gitignore..."
cat >> .gitignore << 'GIT'

# Development artifacts
*ACHIEVEMENTS.md
AGENT_MEMORY.md
*.backup
swarm_outputs/
orchestration_iterations/
autonomous_development/
.env
__pycache__/
*.py[cod]
.pytest_cache/
htmlcov/
GIT
echo "  .gitignore updated."

echo "→ Phase 1: Removing requirements.txt..."
if [ -f "requirements.txt" ]; then
    git rm --cached requirements.txt 2>/dev/null || true
    rm -f requirements.txt
    echo "  Removed requirements.txt (pyproject.toml is the single source of truth)"
fi

echo "→ Phase 1: Placing CLAUDE.md in repo root..."
if [ ! -f "CLAUDE.md" ]; then
    echo "  NOTE: Copy CLAUDE.md from the plan deliverables into this repo root."
    echo "  It bridges your Claude.ai planning session into Claude Code."
fi

# ─────────────────────────────────────────
# GIT COMMIT + PUSH
# ─────────────────────────────────────────

echo ""
echo "→ Staging all changes..."
git add -A

echo "→ Committing Phase 0 + Phase 1..."
git commit -m "fix+chore: Phase 0 security fixes and Phase 1 repo cleanup

Phase 0 — Security:
- Flask debug=False, bind to localhost by default (env-configurable)
- Add .env.example with safe defaults
- [manual] Replace bare except handlers (see warnings above)

Phase 1 — Cleanup:
- Remove development diary files (TONIGHT_ACHIEVEMENTS, SESSION_ACHIEVEMENTS, AGENT_MEMORY)
- Remove PROJECT_SUMMARY.md, README.md.backup, README_BADGES.txt
- Move 132 generated modules to candidates/ (not deleted, awaiting validation gate)
- Add candidates/README.md explaining the validation gate process
- Move shell scripts to scripts/dev/ and scripts/docker/
- Move analyzer tools to tools/
- Remove requirements.txt (pyproject.toml is single source of truth)
- Update .gitignore for dev artifacts
- Add CLAUDE.md for Claude Code context persistence

Next: Phase 2 — Architecture overhaul (BaseScanner, FastAPI, SQLite, Typer CLI)"

echo "→ Pushing to origin main..."
git push origin main

echo ""
echo "=== Done. ==="
echo ""
echo "Next steps:"
echo "  1. Fix any bare except: handlers flagged above (manual)"
echo "  2. Update README.md to honest state (3 scanners, alpha)"
echo "  3. Add first real entry to CHANGELOG.md"
echo "  4. Start Phase 2: create src/daqiq/core/base_scanner.py"
