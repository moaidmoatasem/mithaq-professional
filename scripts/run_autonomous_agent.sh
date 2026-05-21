#!/bin/bash
# Master Script - Run Agents Autonomously

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🤖 cherenkov AUTONOMOUS AGENT SYSTEM                         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo

# Check what iteration to run next
LAST_ITERATION=$(ls cherenkov-professional/scripts/swarm_iteration_*.py 2>/dev/null | tail -1)
if [[ $LAST_ITERATION =~ iteration_([0-9]+) ]]; then
    NEXT=$((${BASH_REMATCH[1]} + 1))
else
    NEXT=1
fi

echo "🔍 Last iteration: ${BASH_REMATCH[1]}"
echo "🚀 Next iteration: $NEXT"
echo

# Check if iteration script exists
ITERATION_SCRIPT="cherenkov-professional/scripts/swarm_iteration_${NEXT}_*.py"

if ls $ITERATION_SCRIPT 1> /dev/null 2>&1; then
    echo "✅ Found iteration script"
    PYTHONPATH=. python $(ls $ITERATION_SCRIPT | head -1)
else
    echo "📝 No iteration $NEXT script found. Creating autonomous iteration..."
    
    # Create a generic autonomous iteration
    cat > "cherenkov-professional/scripts/swarm_iteration_${NEXT}_auto.py" << 'PYTHON'
#!/usr/bin/env python3
"""Auto-generated autonomous iteration"""
import sys
sys.path.insert(0, '.')

print(f"🤖 Running autonomous iteration #{NEXT}")
print("Let me analyze what needs to be done...")

# Agents will analyze and build autonomously here
PYTHON
    
    echo "✅ Created swarm_iteration_${NEXT}_auto.py"
    echo "🎯 Run it to let agents decide what to build!"
fi

echo
echo "════════════════════════════════════════════════════════════"

