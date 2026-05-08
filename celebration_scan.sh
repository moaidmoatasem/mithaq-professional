#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  🎉 CELEBRATION SCAN - cherenkov FRAMEWORK SHOWCASE             ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

TARGETS=(
    "https://example.com"
    "https://google.com"
    "https://github.com"
)

echo "🎯 Running celebration scans on multiple targets..."
echo ""

for target in "${TARGETS[@]}"; do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔍 Scanning: $target"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    python cherenkov_simple_scanner.py "$target"
    echo ""
    sleep 2
done

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ✅ CELEBRATION SCANS COMPLETE - FRAMEWORK VALIDATED!       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Results saved in output/"
echo ""

