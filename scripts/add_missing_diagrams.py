#!/usr/bin/env python3
"""Add basic Mermaid diagrams to architecture docs missing them."""

import os
from pathlib import Path

ARCHITECTURE_DIR = Path("docs/architecture")
BASIC_DIAGRAM = '''```mermaid
graph TD
    A[Component] --> B[Subcomponent]
    B --> C[Implementation Detail]
```
'''

def add_diagram_if_missing(file_path):
    content = file_path.read_text()
    if '```mermaid' not in content:
        print(f"Adding diagram to: {file_path.name}")
        updated_content = content + "\n" + BASIC_DIAGRAM
        file_path.write_text(updated_content)
        return True
    return False

def main():
    added_count = 0
    for md_file in ARCHITECTURE_DIR.glob("*.md"):
        if add_diagram_if_missing(md_file):
            added_count += 1

    print(f"Added diagrams to {added_count} files")

if __name__ == "__main__":
    main()