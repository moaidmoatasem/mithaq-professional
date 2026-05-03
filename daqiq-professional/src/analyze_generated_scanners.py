#!/usr/bin/env python3
"""
Analyze and test AI-generated scanner code
"""

import os
from pathlib import Path

scanner_dir = Path("daqiq/scanners/generated")

print("=" * 70)
print("🔍 ANALYZING AI-GENERATED SCANNERS")
print("=" * 70)

# Check Python files
python_files = list(scanner_dir.glob("*.py"))
print(f"\n📦 Found {len(python_files)} Python scanner files:")

for scanner in python_files:
    if scanner.name == "__init__.py":
        continue

    print(f"\n{'='*70}")
    print(f"📄 {scanner.name}")
    print("=" * 70)

    with open(scanner, "r") as f:
        content = f.read()
        lines = content.count("\n")

        # Check for key components
        has_imports = "import" in content
        has_function = "def " in content
        has_class = "class " in content
        has_requests = "requests" in content.lower()
        has_error_handling = "try:" in content or "except" in content

        print(f"Lines: {lines}")
        print(f"✓ Imports: {has_imports}")
        print(f"✓ Functions: {has_function}")
        print(f"✓ Classes: {has_class}")
        print(f"✓ HTTP Requests: {has_requests}")
        print(f"✓ Error Handling: {has_error_handling}")

        # Show first 30 lines
        print(f"\n📖 Preview (first 30 lines):")
        print("-" * 70)
        lines_list = content.split("\n")[:30]
        for i, line in enumerate(lines_list, 1):
            print(f"{i:3d} | {line}")

# Check batch text files for additional context
print("\n" + "=" * 70)
print("📋 BATCH OUTPUT FILES")
print("=" * 70)

batch_files = list(scanner_dir.glob("batch_*.txt"))
for batch in sorted(batch_files):
    size = batch.stat().st_size
    print(f"  • {batch.name} ({size:,} bytes)")

print("\n" + "=" * 70)
print("✅ Analysis complete!")
print("=" * 70)
