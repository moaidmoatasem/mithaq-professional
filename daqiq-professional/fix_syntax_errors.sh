#!/bin/bash
echo "🔧 Finding and removing files with syntax errors..."

BROKEN=0
VALID=0

for file in $(find src/daqiq/autonomous_generated -name "*.py" -type f); do
    if python -m py_compile "$file" 2>/dev/null; then
        ((VALID++))
    else
        echo "  ❌ Removing broken: $file"
        rm "$file"
        ((BROKEN++))
    fi
done

echo ""
echo "✅ Cleanup complete!"
echo "  Valid files: $VALID"
echo "  Removed broken files: $BROKEN"
