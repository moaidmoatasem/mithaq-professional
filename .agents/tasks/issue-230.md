# Task: Issue #230 — Remove cloud deployment configs violating MEISSNER invariant

**Branch:** `fix/230-meissner-cloud-configs`
**Labels:** `priority:critical, security, phase-2`
**Milestone:** v1.1.0
**PR must contain:** `Closes #230`

## Context

The MEISSNER invariant mandates zero outbound calls outside the scan target. Cloud deployment
configs (Cloudflare Workers) in the repo root violate this principle. These must be removed or
archived to prevent accidental cloud egress deployments.

## Context files

```
wrangler.jsonc          ← Cloudflare Workers config (root) — DELETE
wrangler.toml           ← Cloudflare Workers config (root) — DELETE
package.json            ← Root package.json — REMOVE if CF-only, else audit
deploy/                 ← Audit for any cloud-egress provider references
deploy/providers/       ← Move cloud configs to archive/cloud-deploy/
```

## What to do

1. **Delete root Cloudflare configs**:
   ```bash
   git rm wrangler.jsonc wrangler.toml
   ```

2. **Audit root `package.json`**:
   - If it exists only for Cloudflare Workers (`wrangler` dependency), delete it
   - If it has other purposes (monorepo workspace config), keep it but remove CF-related deps/scripts

3. **Audit `deploy/` directory**:
   ```bash
   grep -r "cloudflare\|wrangler\|workers\|aws\|gcp\|azure\|heroku" deploy/
   ```
   - Move any cloud provider configs to `archive/cloud-deploy/`
   - Keep only local/on-prem deployment configs (Docker, k8s for local)

4. **Audit for remaining cloud egress references**:
   ```bash
   grep -rn "cloudflare\|wrangler\|workers\.dev" packages/ scripts/ --include='*.py' --include='*.ts' --include='*.json'
   ```
   - Remove or comment out any cloud-egress code paths

5. **Add comment in MEISSNER section** of any relevant config files to prevent re-introduction

## Files to modify

- `wrangler.jsonc` — DELETE
- `wrangler.toml` — DELETE
- `package.json` — AUDIT & possibly DELETE
- `deploy/providers/` — MOVE cloud configs to `archive/cloud-deploy/`
- `deploy/` — AUDIT all files

## Verify

```bash
# Confirm wrangler files are gone
test ! -f wrangler.jsonc && test ! -f wrangler.toml && echo "PASS: wrangler removed"

# Confirm no cloud egress references in active code
grep -rn "cloudflare\|wrangler\|workers\.dev" packages/ scripts/ --include='*.py' --include='*.ts' && echo "FAIL" || echo "PASS: no cloud refs"

# Lint
ruff format packages/ && ruff check packages/ --ignore W,S,B
```
