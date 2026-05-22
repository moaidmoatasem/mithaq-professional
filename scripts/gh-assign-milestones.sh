#!/bin/bash
# Assign milestones + sprint labels to all 18 open issues
cd /home/moaid/cherenkov-professional

echo "=== Assigning milestones to open issues ==="

# Phase 2 issues → v1.1.0 milestone (#5)
for n in 230 231 232 233 234 235 236 237 238 239; do
  gh issue edit "$n" --milestone "v1.1.0" 2>/dev/null && echo "  #$n → v1.1.0" || echo "  #$n FAILED"
done

# Phase 3 issues → v1.5.0 milestone (#6)
for n in 240 241 242 243 244 245 246 247; do
  gh issue edit "$n" --milestone "v1.5.0" 2>/dev/null && echo "  #$n → v1.5.0" || echo "  #$n FAILED"
done

echo ""
echo "=== Adding sprint labels ==="

# Sprint 3 (current): P0 blockers + critical infra
for n in 230 232 234 239; do
  gh issue edit "$n" --add-label "sprint-2" 2>/dev/null && echo "  #$n → sprint-2" || echo "  #$n FAILED"
done

# Scanner graduation wave
for n in 240 241 245; do
  gh issue edit "$n" --add-label "sprint-2" 2>/dev/null && echo "  #$n → sprint-2" || echo "  #$n FAILED"
done

echo ""
echo "=== Marking in-progress ==="
for n in 232 230; do
  gh issue edit "$n" --add-label "status:in-progress" 2>/dev/null && echo "  #$n → in-progress" || echo "  #$n FAILED"
done

echo ""
echo "=== Done ==="
gh issue list --state open --limit 20 --json number,title,milestone --jq '.[] | "#" + (.number|tostring) + " [" + (.milestone.title // "NONE") + "] " + .title'
