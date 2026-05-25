#!/bin/sh
# check-docs-drift.sh — enforce the Documentation Mandate.
#
# Fails if a PR touches a documented surface (API routes, storage, auth/CSRF
# middleware) without a corresponding change under cherno-docs/. Honors the
# rule defined in AGENTS.md (Documentation Mandate, Non-Negotiable) and the
# guide at cherno-docs/src/content/docs/contributing/documentation.md.
#
# Usage:
#   scripts/check-docs-drift.sh              # compares HEAD against origin/main
#   BASE=origin/develop scripts/check-docs-drift.sh
#
# Exit codes:
#   0  no drift
#   1  documented surface changed without a doc update
#   2  invocation error (git not available, no base ref, etc.)

set -eu

BASE="${BASE:-origin/main}"

if ! command -v git >/dev/null 2>&1; then
  echo "check-docs-drift: git not available" >&2
  exit 2
fi

# Resolve the comparison range. In CI, fetch the base ref if missing.
if ! git rev-parse --verify --quiet "$BASE" >/dev/null; then
  git fetch --no-tags --depth=50 origin "${BASE#origin/}" >/dev/null 2>&1 || true
fi
if ! git rev-parse --verify --quiet "$BASE" >/dev/null; then
  echo "check-docs-drift: cannot resolve base ref '$BASE'" >&2
  exit 2
fi

CHANGED="$(git diff --name-only "$BASE"...HEAD)"

# Surfaces that MUST be reflected in docs when they change.
DOCUMENTED_SURFACE='^(packages/cherenkov/api/|packages/cherenkov/core/storage/|packages/cherenkov/api/middleware/)'
DOCS_PATH='^cherno-docs/src/content/docs/'

CODE_HITS="$(printf '%s\n' "$CHANGED" | grep -E "$DOCUMENTED_SURFACE" || true)"
DOC_HITS="$(printf '%s\n' "$CHANGED" | grep -E "$DOCS_PATH" || true)"

if [ -z "$CODE_HITS" ]; then
  echo "check-docs-drift: no documented surfaces changed — OK"
  exit 0
fi

if [ -n "$DOC_HITS" ]; then
  echo "check-docs-drift: documented surface changed and docs updated — OK"
  exit 0
fi

cat >&2 <<EOF
check-docs-drift: documentation drift detected.

The following files touch a documented surface but no file under
cherno-docs/src/content/docs/ was updated in this branch:

$CODE_HITS

The Documentation Mandate (AGENTS.md) requires that any PR changing a public
API, endpoint, env var, role, invariant, schema, or operational procedure
update cherno-docs/ in the same commit.

See: cherno-docs/src/content/docs/contributing/documentation.md
EOF

exit 1
