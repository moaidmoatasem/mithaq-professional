#!/bin/bash

TARGETS=(
    "https://google.com"
    "https://github.com"
    "https://stackoverflow.com"
    "https://reddit.com"
    "https://twitter.com"
)

echo "🔍 Starting batch security scan..."
echo "Targets: ${#TARGETS[@]}"
echo ""

for url in "${TARGETS[@]}"; do
    echo "Scanning: $url"
    python cherenkov_simple_scanner.py "$url"
    echo ""
    sleep 2  # Be nice to servers
done

echo "✅ Batch scan complete!"
echo "📁 Check scan_report_*.json files"

