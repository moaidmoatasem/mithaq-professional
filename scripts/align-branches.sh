#!/usr/bin/env bash
# Rebase every local branch onto origin/main.
# - Skips branches checked out in any worktree (cannot be checked out here).
# - On conflict: aborts the rebase and records the branch.
# - Does NOT push. After review, force-push individual branches manually.
#
# Run from inside WSL (native ext4), not via the \\wsl.localhost UNC mount.

set -uo pipefail

cd "$(git rev-parse --show-toplevel)"

START_BRANCH=$(git rev-parse --abbrev-ref HEAD)
LOG_DIR=".git/align-log"
mkdir -p "$LOG_DIR"
OK_LOG="$LOG_DIR/rebased-ok.txt"
CONFLICT_LOG="$LOG_DIR/conflicts.txt"
SKIP_LOG="$LOG_DIR/skipped.txt"
: > "$OK_LOG"; : > "$CONFLICT_LOG"; : > "$SKIP_LOG"

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "ERROR: working tree dirty. Commit or stash first." >&2
  exit 1
fi

echo "==> Fetching origin"
git fetch origin --prune

# Map branch -> worktree path (for branches checked out elsewhere, including this one).
# We rebase pinned branches INSIDE their own worktree so they don't silently drift.
#
# Translate Windows-style paths git may have stored (worktrees added from VS Code /
# Kilo on Windows). //wsl.localhost/<distro>/home/X -> /home/X. C:/... is unreachable
# from WSL and we mark it as such.
translate_path() {
  local p="$1"
  # //wsl.localhost/<distro>/path  OR  //wsl$/<distro>/path  -> /path
  if [[ "$p" =~ ^//wsl(\.localhost|\$)/[^/]+(/.*)$ ]]; then
    echo "${BASH_REMATCH[2]}"
    return
  fi
  # Drive-letter Windows path (C:/..., D:\...) — not reachable from WSL.
  if [[ "$p" =~ ^[A-Za-z]:[/\\] ]]; then
    echo "__UNREACHABLE__"
    return
  fi
  echo "$p"
}

declare -A WT_PATH
while IFS= read -r line; do
  case "$line" in
    worktree\ *) cur_path=$(translate_path "${line#worktree }") ;;
    branch\ *) br_ref="${line#branch }"; WT_PATH["${br_ref#refs/heads/}"]="$cur_path" ;;
  esac
done < <(git worktree list --porcelain)

THIS_WT=$(translate_path "$(git rev-parse --show-toplevel)")
BASE="origin/main"
echo "==> Rebasing local branches onto $BASE"

while IFS= read -r br; do
  br="${br#\* }"; br="${br# }"
  [[ -z "$br" ]] && continue
  [[ "$br" == "main" ]] && { echo "  skip main"; echo "$br" >> "$SKIP_LOG"; continue; }

  pinned_at="${WT_PATH[$br]:-}"

  if [[ "$pinned_at" == "__UNREACHABLE__" ]]; then
    echo "-- $br  (worktree on Windows drive — unreachable from WSL)"
    echo "$br (unreachable Windows worktree)" >> "$SKIP_LOG"
    continue
  fi

  if [[ -n "$pinned_at" && "$pinned_at" != "$THIS_WT" ]]; then
    # Rebase inside the worktree where this branch is checked out.
    echo "-- $br  (in worktree: $pinned_at)"
    if [[ ! -d "$pinned_at" ]]; then
      echo "  skip — worktree path not found"
      echo "$br (worktree path missing: $pinned_at)" >> "$SKIP_LOG"
      continue
    fi
    if ! (cd "$pinned_at" && git diff --quiet && git diff --cached --quiet); then
      echo "  skip — worktree dirty"
      echo "$br (worktree dirty: $pinned_at)" >> "$SKIP_LOG"
      continue
    fi
    if (cd "$pinned_at" && git rebase -q "$BASE"); then
      echo "  ok (worktree)"
      echo "$br" >> "$OK_LOG"
    else
      (cd "$pinned_at" && git rebase --abort 2>/dev/null)
      echo "  CONFLICT — aborted (worktree)"
      echo "$br" >> "$CONFLICT_LOG"
    fi
    continue
  fi

  if [[ -n "$pinned_at" && "$pinned_at" == "$THIS_WT" ]]; then
    # Current worktree's own branch — rebase in place (already checked out).
    echo "-- $br  (current worktree)"
    if git rebase -q "$BASE"; then
      echo "  ok"
      echo "$br" >> "$OK_LOG"
    else
      git rebase --abort 2>/dev/null
      echo "  CONFLICT — aborted"
      echo "$br" >> "$CONFLICT_LOG"
    fi
    continue
  fi

  # Unpinned branch — checkout here and rebase.
  echo "-- $br"
  if ! git checkout -q "$br" 2>/dev/null; then
    echo "  checkout failed"
    echo "$br (checkout failed)" >> "$SKIP_LOG"
    continue
  fi
  if git rebase -q "$BASE"; then
    echo "  ok"
    echo "$br" >> "$OK_LOG"
  else
    git rebase --abort 2>/dev/null
    echo "  CONFLICT — aborted"
    echo "$br" >> "$CONFLICT_LOG"
  fi
done < <(git for-each-ref --format='%(refname:short)' refs/heads/)

echo "==> Restoring $START_BRANCH"
git checkout -q "$START_BRANCH"

echo
echo "==> Summary"
echo "  rebased  : $(wc -l < "$OK_LOG")  (see $OK_LOG)"
echo "  conflict : $(wc -l < "$CONFLICT_LOG")  (see $CONFLICT_LOG)"
echo "  skipped  : $(wc -l < "$SKIP_LOG")  (see $SKIP_LOG)"
echo
echo "Nothing was pushed. Review, then force-push selectively:"
echo "  git push --force-with-lease origin <branch>"
