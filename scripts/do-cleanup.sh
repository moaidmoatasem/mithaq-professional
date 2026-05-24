#!/bin/bash
set -euo pipefail
cd /home/moaid/cherenkov-professional
git checkout fix/223-root-cleanup

mkdir -p archive/legacy scripts/output tests/legacy

# Delete junk files
for f in "=12.0" "=2.31.0" test_export test_session validation_report.txt; do
  if [ -e "$f" ]; then
    git rm -f "$f" 2>/dev/null || rm -f "$f"
    echo "  deleted $f"
  fi
done

# Move scripts to scripts/
for f in patch_base_agent_tools.py proxy_server.py test_api.sh; do
  if [ -f "$f" ]; then
    git mv "$f" scripts/
    echo "  moved $f -> scripts/"
  fi
done

# Move legacy dirs to archive/
for d in dev_crew workflow_results; do
  if [ -d "$d" ]; then
    git mv "$d" archive/
    echo "  moved $d/ -> archive/"
  fi
done

# Move unused configs to archive/
for f in wrangler.jsonc wrangler.toml DVWA_REPORT.md; do
  if [ -f "$f" ]; then
    git mv "$f" archive/
    echo "  moved $f -> archive/"
  fi
done

git add -A
git commit -m "chore(infra): deep root cleanup — remove junk, archive legacy (#223)

Closes #223
Co-Authored-By: Antigravity <noreply@google.com>"

echo ""
echo "Root items now: $(ls -1 | wc -l)"
ls -1
echo ""
echo "Done. Push with: git push -u origin fix/223-root-cleanup"
