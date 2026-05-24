#!/bin/bash
cd /home/moaid/cherenkov-professional

echo "=== OPEN ISSUES ==="
gh issue list --state open --limit 50 --json number,title,labels,milestone

echo "=== OPEN PRs ==="
gh pr list --state open --json number,title,labels,headRefName

echo "=== MILESTONES ==="
gh api repos/moaidmoatasem/cherenkov-professional/milestones --jq '.[] | "#" + (.number|tostring) + " " + .title + " [" + .state + "] open=" + (.open_issues|tostring)'

echo "=== LABELS ==="
gh label list --limit 50
