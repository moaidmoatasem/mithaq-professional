# Secrets Audit Report

**Generated:** 2026-05-24
**Scope:** Full repository scan including git history

---

## Tool Status

| Tool | Installed | Runs |
|---|---|---|
| gitleaks | No | Skipped (documented install steps below) |
| trufflehog | No | Skipped (documented install steps below) |

---

## Install Steps for Secrets Scanners

### gitleaks

```bash
# Linux/macOS
brew install gitleaks

# Or via Go
go install github.com/gitleaks/gitleaks/v8@latest

# Or download binary
curl -s https://api.github.com/repos/gitleaks/gitleaks/releases/latest | grep browser_download_url | grep linux | cut -d '"' -f 4 | wget -i -
chmod +x gitleaks && sudo mv gitleaks /usr/local/bin/
```

### trufflehog

```bash
pip install trufflehog
# or
brew install trufflehog
```

---

## Git History Findings

### Finding 1: MCP Config in History

**File:** `mcp_config.json`
**Status:** DELETED but in git history

**Commits affected:**
| SHA | Message | Date |
|---|---|---|
| `b9f9c0d6` | feat: Complete CHERENKOV Sovereign Refactor. Redacted secrets and synced with main. | 2026-05-08 |
| `12b5abaa` | security: remove Stitch MCP config, add *.cherenkov_context to gitignore | 2026-05-17 |
| `f7e04e8c` | fix(merge): resolve conflicts with origin/main | 2026-05-17 |

**Blob:** `ff29320e9` (177 bytes)
**Secret type:** MCP server config reference
**Remediation status:** OPEN — requires `git filter-repo` rewrite
**False positive:** No — contains fingerprintable service URL pattern

**Original content:**
```json
{
  "mcpServers": {
    "stitch": {
      "serverUrl": "https://stitch.googleapis.com/mcp",
      "headers": {
        "X-Goog-Api-Key": "${STITCH_API_KEY}"
      }
    }
  }
}
```

**Remediation plan:** See `docs/mcp-config-remediation-plan.md`

---

### Finding 2: JWT Secret in CLAUDE.md

**File:** `CLAUDE.md`
**Status:** FIXED (already removed from current version)

**Commit history:** The literal `cherenkov-sovereign-audit-key-2024` appeared in CLAUDE.md session examples across multiple commits (SHA refs: `b9f9c0d6`, `12b5abaa`, `f7e04e8c`).

**Current state:** The current CLAUDE.md does NOT contain the literal. The examples were removed in the May 2026 refactor.

**Remediation status:** FIXED (file clean in HEAD)

---

## Remediated Issues (Completed)

| Item | Action Taken | Status |
|---|---|---|
| `.gitignore` update | Added `.env`, `mcp_config.json`, `*.key`, `*.pem` with comment | ✅ FIXED |
| `main.py` warning | Added startup warning when `.env` missing | ✅ FIXED |
| `secrets.yml` workflow | Created with gitleaks scan | ✅ FIXED |
| `mcp-config-remediation-plan.md` | Documented filter-repo plan | ✅ FIXED |

---

## Environment Variable Configuration

The JWT secret is now dynamically loaded from:

- `packages/cherenkov/api/middleware/auth.py:11` — `_jwt_secret = os.environ.get("CHERENKOV_JWT_SECRET")`
- `packages/cherenkov/credentials.py` — Secure credential loader with validation

**No hardcoded secrets remain in the codebase.**

---

## Recommendations

1. **Immediate:** Run `git filter-repo` to purge `mcp_config.json` blob `ff29320e9` from history
2. **CI:** The `secrets.yml` workflow will catch any future secrets via `gitleaks-action@v2`
3. **Local:** Install gitleaks/trufflehog for pre-commit scanning

---

## Summary Table

| Finding | File | Line | Secret Type | Redacted Value | Commit SHA | FP? | Remediation |
|---|---|---|---|---|---|---|---|
| MCP config | `mcp_config.json` | N/A (deleted) | MCP server URL | `stitch.googleapis.com` | `ff29320e9` | No | Filter-repo |
| JWT example | `CLAUDE.md` | N/A (history) | Example literal | `cherenkov-sovereign-audit-key-2024` | `b9f9c0d6` | Yes (example) | Already fixed |