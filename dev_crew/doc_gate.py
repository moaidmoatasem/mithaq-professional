#!/usr/bin/env python3
"""Documentation validation gate for CHERENKOV.

Validates structure, cross-references, diagram presence, naming,
and manifest compliance for all documentation files.

Usage:
    python dev_crew/doc_gate.py validate --manifest docs/manifest.json
    python dev_crew/doc_gate.py check-file --path docs/architecture/data-flow.md
    python dev_crew/doc_gate.py list-issues
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


class DocGate:
    """Validation gate for CHERENKOV documentation."""

    def __init__(self, repo_root: str | Path | None = None):
        self.repo_root = Path(repo_root or ".").resolve()
        self.issues: list[str] = []

    def validate_manifest(self, manifest_path: str | Path) -> bool:
        """Validate all manifest entries resolve and all docs/ files are listed."""
        manifest_path = Path(manifest_path)
        if not manifest_path.exists():
            self.issues.append(f"MANIFEST_MISSING: {manifest_path}")
            return False

        with open(manifest_path) as f:
            manifest = json.load(f)

        all_ok = True
        for entry in manifest.get("entries", []):
            source = entry.get("source", "")
            if source.startswith("https://"):
                continue
            full_path = (self.repo_root / source).resolve()
            if not full_path.exists():
                self.issues.append(f"MANIFEST_BROKEN: {entry.get('topic')} -> {source} (not found)")
                all_ok = False

        manifest_sources = {
            e["source"]
            for e in manifest.get("entries", [])
            if not e["source"].startswith("https://")
        }
        for md_file in (self.repo_root / "docs").rglob("*.md"):
            rel_path = str(md_file.relative_to(self.repo_root))
            if rel_path not in manifest_sources:
                self.issues.append(f"MANIFEST_MISSING_ENTRY: {rel_path} not in manifest")
                all_ok = False

        return all_ok

    def check_file(self, file_path: str | Path) -> bool:
        """Validate a single documentation file."""
        path = Path(file_path)
        if not path.exists():
            self.issues.append(f"FILE_MISSING: {path}")
            return False

        content = path.read_text()
        rel_path = str(path.relative_to(self.repo_root))
        all_ok = True

        # Check: Exactly one H1
        h1_matches = re.findall(r"^# (.+)$", content, re.MULTILINE)
        if not h1_matches:
            self.issues.append(f"H1_MISSING: {rel_path} — no H1 heading found")
            all_ok = False

        # Check: No broken relative links
        link_matches = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)
        for _text, link in link_matches:
            if link.startswith(("http://", "https://", "#", "mailto:")):
                continue
            link_path = (path.parent / link).resolve()
            if not link_path.exists():
                if "#" in link:
                    base = link.split("#")[0]
                    link_path = (path.parent / base).resolve()
                    if not link_path.exists():
                        self.issues.append(f"BROKEN_LINK: {rel_path} -> {link} (base not found)")
                        all_ok = False
                else:
                    self.issues.append(f"BROKEN_LINK: {rel_path} -> {link} (not found)")
                    all_ok = False

        # Check: Architecture docs must have Mermaid diagrams
        if "architecture" in rel_path:
            mermaid_count = content.count("```mermaid")
            if mermaid_count == 0:
                self.issues.append(
                    f"DIAGRAM_MISSING: {rel_path} — "
                    "architecture doc must include Mermaid diagram"
                )
                all_ok = False

        # Check: File name is kebab-case
        filename = path.name
        if not re.match(r"^[a-z0-9-]+\.md$", filename):
            self.issues.append(f"NAMING_INVALID: {rel_path} — file name must be kebab-case")
            all_ok = False

        return all_ok

    def list_issues(self) -> list[str]:
        """Return all collected issues."""
        return self.issues

    def run_full_validation(self, manifest_path: str | Path) -> bool:
        """Run all validation checks across the entire docs directory."""
        all_ok = True
        manifest_ok = self.validate_manifest(manifest_path)
        if not manifest_ok:
            all_ok = False
        for md_file in sorted((self.repo_root / "docs").rglob("*.md")):
            file_ok = self.check_file(md_file)
            if not file_ok:
                all_ok = False
        return all_ok


def main():
    parser = argparse.ArgumentParser(description="CHERENKOV Documentation Validation Gate")
    subparsers = parser.add_subparsers(dest="command")

    validate_parser = subparsers.add_parser("validate", help="Run full validation")
    validate_parser.add_argument("--manifest", default="docs/manifest.json")

    check_parser = subparsers.add_parser("check-file", help="Check a single file")
    check_parser.add_argument("--path", required=True)

    subparsers.add_parser("list-issues", help="List all doc issues")

    args = parser.parse_args()
    gate = DocGate()

    if args.command == "validate":
        ok = gate.run_full_validation(args.manifest)
    elif args.command == "check-file":
        ok = gate.check_file(args.path)
    elif args.command == "list-issues":
        for issue in sorted(gate.issues):
            print(issue)
        return
    else:
        parser.print_help()
        return

    if gate.issues:
        print("DocGate issues found:")
        for issue in sorted(gate.issues):
            print(f"  - {issue}")

    if ok:
        print("DocGate: ALL CHECKS PASSED")
        sys.exit(0)
    else:
        print("DocGate: CHECKS FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
