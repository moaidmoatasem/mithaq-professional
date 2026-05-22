#!/bin/bash
cd /home/moaid/cherenkov-professional

echo "=== MILESTONES ==="
gh api repos/moaidmoatasem/cherenkov-professional/milestones --jq '.[] | .title + " | open=" + (.open_issues|tostring) + " closed=" + (.closed_issues|tostring)'

echo ""
echo "=== ISSUES NEEDING MILESTONE ==="
gh issue list --state open --limit 50 --json number,title,milestone --jq '.[] | select(.milestone == null) | "#" + (.number|tostring) + " " + .title'
