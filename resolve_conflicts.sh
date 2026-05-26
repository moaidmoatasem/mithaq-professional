#!/bin/bash
# ==============================================================================
# CHERENKOV · Automated PR #396 Conflict Resolver
# ==============================================================================
# This script resolves the committed conflict markers in cherno-docs/package.json
# on the branch chore/task-003-blocked-8880436973978031884 and pushes the fix.
# ==============================================================================

set -e

BRANCH="chore/task-003-blocked-8880436973978031884"

echo "=== [1/5] Fetching remote updates ==="
git fetch origin

echo "=== [2/5] Checking out branch $BRANCH ==="
# Ensure the local branch exists and track the remote branch
if git show-ref --quiet --verify "refs/heads/$BRANCH"; then
    git checkout "$BRANCH"
    git reset --hard "origin/$BRANCH"
else
    git checkout -b "$BRANCH" "origin/$BRANCH"
fi

echo "=== [3/5] Resolving conflict markers in cherno-docs/package.json ==="
mkdir -p cherno-docs
cat << 'EOF' > cherno-docs/package.json
{
  "name": "cherno-docs",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "astro dev",
    "start": "astro dev",
    "build": "astro check && astro build",
    "preview": "astro preview",
    "astro": "astro"
  },
  "dependencies": {
    "@astrojs/starlight": "^0.32.1",
    "astro": "^5.0.0",
    "typescript": "^5.9.3"
  }
}
EOF

echo "=== [4/5] Staging, committing, and pushing the resolution ==="
git add cherno-docs/package.json
git commit -m "chore: resolve package.json conflicts in cherno-docs" || echo "No changes to commit (already resolved)"
git push origin "$BRANCH"

echo "=== [5/5] Returning to original branch (main) ==="
git checkout main

echo "=============================================================================="
echo "✔ SUCCESS: PR #396 conflicts resolved and pushed successfully!"
echo "=============================================================================="
