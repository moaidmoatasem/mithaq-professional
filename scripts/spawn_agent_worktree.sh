#!/usr/bin/env bash
# spawn_agent_worktree.sh — create an isolated worktree for an agent task.
#
# Worktrees are named by TASK SLUG, not by agent identity. This means when
# one agent's token expires mid-task, another agent can `cd` into the same
# worktree and continue — no ownership change, no merge conflict.
#
# Usage:
#   scripts/spawn_agent_worktree.sh <task-slug> [base-branch]
#
# Example:
#   scripts/spawn_agent_worktree.sh auth-refactor
#   scripts/spawn_agent_worktree.sh scanner-cve-2024-1234 main
#
# What it does:
#   1. Fetches origin/<base-branch> (default: main)
#   2. Creates ../cherenkov-worktrees/<slug>/ checked out to ai/<slug>
#   3. Rebases on origin/<base-branch> if the branch already existed
#   4. Prints the cd command to enter it

set -euo pipefail

SLUG="${1:-}"
BASE="${2:-main}"

if [[ -z "$SLUG" ]]; then
  echo "usage: $0 <task-slug> [base-branch]" >&2
  exit 2
fi

if ! [[ "$SLUG" =~ ^[a-z0-9][a-z0-9-]{1,48}$ ]]; then
  echo "error: slug must be lowercase, kebab-case, 2-49 chars (got: $SLUG)" >&2
  exit 2
fi

REPO_ROOT="$(git rev-parse --show-toplevel)"
WORKTREE_ROOT="$(dirname "$REPO_ROOT")/cherenkov-worktrees"
WORKTREE_PATH="$WORKTREE_ROOT/$SLUG"
BRANCH="ai/$SLUG"

mkdir -p "$WORKTREE_ROOT"

echo "→ Fetching origin/$BASE..."
git -C "$REPO_ROOT" fetch origin "$BASE" --quiet

if git -C "$REPO_ROOT" worktree list --porcelain | grep -q "^worktree $WORKTREE_PATH$"; then
  echo "→ Worktree already exists at $WORKTREE_PATH — reusing."
  echo "→ Rebasing on origin/$BASE..."
  git -C "$WORKTREE_PATH" fetch origin "$BASE" --quiet
  if ! git -C "$WORKTREE_PATH" rebase "origin/$BASE"; then
    echo "✗ Rebase conflict in $WORKTREE_PATH" >&2
    echo "  Resolve manually or open a GitHub issue with label 'claim/blocked'." >&2
    exit 1
  fi
elif git -C "$REPO_ROOT" show-ref --verify --quiet "refs/heads/$BRANCH"; then
  echo "→ Branch $BRANCH exists locally — attaching worktree."
  git -C "$REPO_ROOT" worktree add "$WORKTREE_PATH" "$BRANCH"
  git -C "$WORKTREE_PATH" rebase "origin/$BASE"
else
  echo "→ Creating worktree $WORKTREE_PATH on new branch $BRANCH..."
  git -C "$REPO_ROOT" worktree add -b "$BRANCH" "$WORKTREE_PATH" "origin/$BASE"
fi

cat <<EOF

✓ Worktree ready.

  Path:    $WORKTREE_PATH
  Branch:  $BRANCH
  Base:    origin/$BASE

Next steps:
  1. Open a claim ticket:
     gh issue create -l claim/active -t "[claim] $SLUG" \\
        -b "Branch: $BRANCH
Files: <list expected files>
Agent: <your identity>"
  2. Enter the worktree:
     cd $WORKTREE_PATH
  3. Work, commit small (≤8 files / ≤400 lines per PR), push, gh pr create.
  4. On merge, close the claim ticket and:
     git worktree remove $WORKTREE_PATH

EOF
