# Task: Issue #231 — Align GitHub repo description, tags, and homepage

**Branch:** `chore/231-repo-metadata`
**Labels:** `priority:medium, chore, phase-2`
**Milestone:** v1.1.0
**PR must contain:** `Closes #231`

## Context

The GitHub repository metadata (description, topics, homepage URL) is stale or missing.
This is a GitHub settings task — primarily `gh` CLI commands, no code changes.

## What to do

1. **Update repo description**:
   ```bash
   gh repo edit moaidmoatasem/cherenkov-professional \
     --description "CHERENKOV — AI-powered security scanning platform with MEISSNER zero-egress architecture"
   ```

2. **Set repository topics/tags**:
   ```bash
   gh repo edit moaidmoatasem/cherenkov-professional \
     --add-topic security,vulnerability-scanner,ai-security,penetration-testing,devsecops,python,fastapi,react
   ```

3. **Set homepage URL** (if applicable, e.g., docs site):
   ```bash
   gh repo edit moaidmoatasem/cherenkov-professional --homepage "https://github.com/moaidmoatasem/cherenkov-professional"
   ```

4. **Verify README badges** match the current CI status and repo metadata

## Files to modify

- No code files — this is a `gh repo edit` task
- Optionally update README.md badges if they reference stale URLs

## Verify

```bash
# Confirm repo metadata updated
gh repo view moaidmoatasem/cherenkov-professional --json description,topics,homepageUrl

# Expected: description, topics array, homepage are set
```
