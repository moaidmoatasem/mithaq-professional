#!/usr/bin/env python3
"""Update manifest.json with missing documentation files."""

import json
from pathlib import Path


def update_manifest():
    manifest_path = Path("docs/manifest.json")
    with open(manifest_path) as f:
        manifest = json.load(f)

    # Get all existing docs files
    docs_dir = Path("docs")
    all_md_files = []
    for md_file in docs_dir.rglob("*.md"):
        rel_path = str(md_file.relative_to(docs_dir.parent))
        all_md_files.append(rel_path)

    # Find files not in manifest
    existing_sources = {e["source"] for e in manifest.get("entries", [])}
    missing_files = [
        f
        for f in all_md_files
        if f not in existing_sources and not f.startswith("docs/governance/")
    ]

    # Add missing files to manifest
    new_entries = []
    for file_path in missing_files:
        # Skip governance files as they're auto-synced
        if "governance/" in file_path:
            continue

        # Determine section from path
        if file_path.startswith("docs/architecture/"):
            section = "architecture"
            topic = (
                file_path.replace("docs/architecture/", "")
                .replace(".md", "")
                .replace("-", " ")
                .title()
            )
        elif file_path.startswith("docs/development/"):
            section = "development"
            topic = (
                file_path.replace("docs/development/", "")
                .replace(".md", "")
                .replace("-", " ")
                .title()
            )
        else:
            section = "misc"
            topic = file_path.replace("docs/", "").replace(".md", "").replace("-", " ").title()

        new_entries.append({"topic": topic, "source": file_path, "section": section})

    if new_entries:
        manifest["entries"].extend(new_entries)
        manifest["last_updated"] = "2026-05-26"

        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        print(f"Added {len(new_entries)} new entries to manifest")
        return True
    else:
        print("No missing files found")
        return False


if __name__ == "__main__":
    update_manifest()
