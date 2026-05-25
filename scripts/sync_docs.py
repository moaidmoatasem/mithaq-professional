#!/usr/bin/env python3
"""Sync bridge for CHERENKOV documentation.

Reads the manifest, validates cross-refs, and syncs root-level
governance files (CODE_OF_CONDUCT.md, CONTRIBUTING.md, SECURITY.md)
into docs/governance/ to keep them in sync.

Usage:
    python scripts/sync_docs.py validate   # Validate only
    python scripts/sync_docs.py sync       # Sync governance files
    python scripts/sync_docs.py status     # Show sync status
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


GOVERNANCE_MAP = {
    "CODE_OF_CONDUCT.md": "docs/governance/code-of-conduct.md",
    "CONTRIBUTING.md": "docs/governance/contributing.md",
    "SECURITY.md": "docs/governance/security.md",
}


def validate_sync(repo_root: Path) -> list[str]:
    """Check which root governance files are out of sync with docs/governance/."""
    issues: list[str] = []
    for src_name, dst_rel in GOVERNANCE_MAP.items():
        src = repo_root / src_name
        dst = repo_root / dst_rel
        if not src.exists():
            issues.append(f"ROOT_MISSING: {src_name} not found at repo root")
            continue
        if not dst.exists():
            issues.append(f"SYNC_NEEDED: {dst_rel} does not exist — needs creation from {src_name}")
            continue
        if file_hash(src) != file_hash(dst):
            issues.append(f"SYNC_NEEDED: {dst_rel} differs from {src_name}")
    return issues


def sync_governance(repo_root: Path) -> list[str]:
    """Sync root governance files into docs/governance/."""
    results: list[str] = []
    for src_name, dst_rel in GOVERNANCE_MAP.items():
        src = repo_root / src_name
        dst = repo_root / dst_rel
        if not src.exists():
            results.append(f"SKIP: {src_name} not found")
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        content = src.read_text()

        # Add a sync notice for docs/ copies
        sync_notice = (
            f"> *This page is auto-synced from [`{src_name}`](https://github.com/"
            f"moaidmoatasem/cherenkov-professional/blob/main/{src_name}). "
            f"Edit that file, not this copy.*\n\n"
        )

        # Check if sync notice already exists
        if not content.startswith(">"):
            content = sync_notice + content

        dst.write_text(content)
        results.append(f"SYNCED: {src_name} -> {dst_rel}")
    return results


def main():
    parser = argparse.ArgumentParser(description="CHERENKOV Documentation Sync Bridge")
    parser.add_argument(
        "command",
        choices=["validate", "sync", "status"],
        help="Command to execute",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root path (default: current dir)",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()

    if args.command == "validate":
        issues = validate_sync(repo_root)
        if issues:
            print("Sync validation issues:")
            for i in issues:
                print(f"  - {i}")
            sys.exit(1)
        else:
            print("All governance files are in sync.")
            sys.exit(0)

    elif args.command == "status":
        issues = validate_sync(repo_root)
        if issues:
            print("Out of sync:")
            for i in issues:
                print(f"  - {i}")
        else:
            print("All governance files are in sync.")

    elif args.command == "sync":
        results = sync_governance(repo_root)
        for r in results:
            print(r)
        issues = validate_sync(repo_root)
        if issues:
            print("\nRemaining issues after sync:")
            for i in issues:
                print(f"  - {i}")


if __name__ == "__main__":
    main()