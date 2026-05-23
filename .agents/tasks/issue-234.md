# Task: Issue #234 — Harden .gitignore

**Branch:** `fix/234-gitignore`
**Labels:** `priority:high, chore, phase-2`
**Milestone:** v1.1.0
**PR must contain:** `Closes #234`

## Context

The `.gitignore` is missing entries for common build artifacts, databases, and
tool-generated files that should never be committed. Sensitive files like SQLite DBs
and agent state directories are at risk of accidental commit.

## What to do

1. **Add the following patterns** to `.gitignore` (if not already present):

   ```gitignore
   # Databases
   *.sqlite
   *.sqlite3
   *.db

   # Node
   node_modules/
   dist/

   # Python build
   *.egg-info/
   __pycache__/
   *.pyc

   # Aider (AI tool)
   .aider*
   .aider.chat.history.md
   .aider.conf.yml
   .aider.input.history
   .aider.tags.cache.v4/

   # Agent state (runtime)
   agent_state/

   # Qdrant vector DB
   qdrant/
   qdrant_storage/

   # MkDocs
   site/

   # Logs
   logs/
   *.log

   # IDE
   .vscode/
   .idea/

   # Virtual environments
   venv/
   .venv/

   # Ruff cache
   .ruff_cache/

   # Pytest cache
   .pytest_cache/
   ```

2. **Remove any already-tracked files** that match new ignore patterns:
   ```bash
   git rm -r --cached .aider* agent_state/ logs/ .ruff_cache/ .pytest_cache/ 2>/dev/null || true
   ```

3. **Keep existing patterns** — only add new ones, don't remove valid existing entries

## Files to modify

- `.gitignore`

## Verify

```bash
# Confirm patterns are present
grep -c "sqlite\|node_modules\|\.aider\|agent_state\|qdrant\|egg-info" .gitignore
# Expected: >= 6

# Confirm no tracked files match new ignore patterns
git status --short | head -20

# Lint (should be unaffected)
ruff format packages/ && ruff check packages/ --ignore W,S,B
```
