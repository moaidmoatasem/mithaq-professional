# MCP Config Remediation Plan

## Background

The file `mcp_config.json` was committed to the repository and later deleted. While the file contents used a placeholder variable `${STITCH_API_KEY}` rather than a live key, the secret variable name and MCP server URL remain in the git history for anyone who can clone the full repo.

**Compliance note:** CHERENKOV Principle 10 ("strip LLM IDs... for every compliant run") requires zero outbound secrets in source history.

---

## Timeline

| Event | Commit SHA | Date | Message |
|---|---|---|---|
| **File introduced** | `b9f9c0d6e3359cf881f06615322c88a58918274a` | 2026-05-08 | `feat: Complete CHERENKOV Sovereign Refactor. Redacted secrets and synced with main.` |
| **File deleted** | `12b5abaa8784e803321bf06ec333432c04eaeecd` | 2026-05-17 | `security: remove Stitch MCP config, add *.cherenkov_context to gitignore` |
| **Merge conflict re-application** | `f7e04e8cbbf34d543e633de93d5fa41c0d4118a1` | 2026-05-17 | `fix(merge): resolve conflicts with origin/main, fix slowapi request param naming` |

---

## Blob Inventory

The deleted file had blob SHA `ff29320e9` (177 bytes).

| Blob SHA | Size | Contents (redacted) |
|---|---|---|
| `ff29320e9`… | 177 B | MCP server config referencing `stitch.googleapis.com` and `${STITCH_API_KEY}` placeholder |

---

## Filter-Repo Plan

### Prerequisites

```bash
# Install git-filter-repo (required, not included with git)
pip install git-filter-repo
# or: brew install git-filter-repo
```

### Full Rewrite

**DO NOT run this on a shared copy without coordinating with all contributors.**

```bash
# 1. Make a fresh bare clone (required for filter-repo safety)
cd /tmp
git clone --mirror /home/moaid/cherenkov-professional cherenkov-scrub.git
cd chernkov-scrub.git

# 2. Rewrite history — remove mcp_config.json blob from all reachable commits
git filter-repo --path mcp_config.json --invert-paths
#   --invert-paths : removes the path, keeps all other objects

# 3. Verify the blob is gone
git cat-file -t ff29320e9   # should print "error: Object not found"
git rev-list --all --objects | grep mcp_config.json    # should return empty

# 4. Replace the local mirror
cd /home/moaid/cherenkov-professional
git remote add scrub /tmp/cherenkov-scrub.git
git fetch scrub
git checkout --force refs/heads/main  # or your branch

# 5. Force-push rewritten history
git push origin --force --all
git push origin --force --tags
```

### Partial Rewrite (if full mirror is impractical)

If the team prefers to retain most history without rewriting all commits:

```bash
# Replace the secret variable placeholder only, keeping the structure
git filter-repo --replace-text <(echo '${STITCH_API_KEY}==>[REDACTED]')
```

**Risk:** The MCP server URL and file structure remain visible. Not recommended for compliance scenarios requiring full secrecy removal.

---

## Post-Write Checklist

- [ ] All local clones are deleted and freshly re-cloned
- [ ] CI secrets (`OPERATOR_API_KEY`) are confirmed present in GitHub → Settings → Secrets
- [ ] All contributors run `git fetch --all && git reset --hard origin/main`
- [ ] `git reflog expire --expire=now --all && git gc --prune=now --aggressive` on old local repos
- [ ] File `mcp_config.json` confirmed absent from `git log --all --full-history -- mcp_config.json`

---

## Note on mcp_config.json Content

The committed file contained only a variable reference, not a live key:

```json
{ "mcpServers": { "stitch": { "serverUrl": "https://stitch.googleapis.com/mcp", "headers": { "X-Goog-Api-Key": "${STITCH_API_KEY}" } } } }
```

This was already partially sanitized, but the variable name `${STITCH_API_KEY}` and the service URL still contain a fingerprintable pattern.
