#!/bin/bash
cd /home/moaid/cherenkov-professional

echo "=== OPEN ISSUES ==="
gh issue list --state open --limit 50 --json number,title,milestone --jq '.[] | "#\(.number) [\(.milestone.title // "NONE")] \(.title)"'

echo ""
echo "=== RECENTLY CLOSED ==="
gh issue list --state closed --limit 15 --json number,title,closedAt --jq '.[] | "#\(.number) [closed \(.closedAt[:10])] \(.title)"'

echo ""
echo "=== OPEN PRs ==="
gh pr list --state open --json number,title,headRefName --jq '.[] | "#\(.number) [\(.headRefName)] \(.title)"'

echo ""
echo "=== RECENT MERGED PRs ==="
gh pr list --state merged --limit 10 --json number,title --jq '.[] | "#\(.number) \(.title)"'

echo ""
echo "=== NEW REMOTE BRANCHES ==="
git branch -r --sort=-committerdate | head -15

echo ""
echo "=== LOCAL BRANCH STATE ==="
git log --oneline -5
