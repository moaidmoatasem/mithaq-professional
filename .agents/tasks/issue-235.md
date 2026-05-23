# Task: Issue #235 — Canonicalize CHANGELOG.md

**Branch:** `chore/235-changelog`
**Labels:** `priority:low, chore, phase-2`
**Milestone:** v1.1.0
**PR must contain:** `Closes #235`

## Context

`CHANGELOG.md` entries may not accurately reflect the actual git history. Entries
should be rewritten to match merged PRs and tagged releases, following Keep a Changelog
format (https://keepachangelog.com/).

## What to do

1. **Audit git history** for actual changes:
   ```bash
   git log --oneline --since="2025-01-01" --no-merges | head -50
   git tag -l
   ```

2. **Rewrite CHANGELOG.md** using Keep a Changelog format:
   ```markdown
   # Changelog

   All notable changes to this project will be documented in this file.
   Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)

   ## [Unreleased]
   ### Added
   - ...
   ### Changed
   - ...
   ### Fixed
   - ...

   ## [v1.0.0] - YYYY-MM-DD
   ### Added
   - ...
   ```

3. **Ensure each entry** references the relevant PR or issue number

4. **Add `[Unreleased]` section** at the top for ongoing work

## Files to modify

- `CHANGELOG.md`

## Verify

```bash
# Confirm structure
head -30 CHANGELOG.md

# Confirm entries have issue/PR references
grep -c "#[0-9]" CHANGELOG.md
```
