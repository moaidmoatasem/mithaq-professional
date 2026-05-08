#!/usr/bin/env python3
"""
Test memory-efficient batched parallel execution
Generates 6 security scanners in 3 batches of 2
"""

from cherenkov.core.memory_efficient_parallel import MemoryEfficientCrew
import sys

# Define 6 different security scanner agents
agent_configs = [
    {
        'role': 'XSS Scanner Developer',
        'goal': 'Write complete XSS vulnerability scanner',
        'backstory': 'Web security expert specializing in XSS detection'
    },
    {
        'role': 'SQL Injection Scanner Developer',
        'goal': 'Write complete SQL injection scanner',
        'backstory': 'Database security expert with SQLi expertise'
    },
    {
        'role': 'CSRF Scanner Developer',
        'goal': 'Write complete CSRF vulnerability scanner',
        'backstory': 'Web application security specialist'
    },
    {
        'role': 'Directory Traversal Scanner Developer',
        'goal': 'Write complete path traversal scanner',
        'backstory': 'File system security expert'
    },
    {
        'role': 'Open Redirect Scanner Developer',
        'goal': 'Write complete open redirect scanner',
        'backstory': 'URL security specialist'
    },
    {
        'role': 'XXE Scanner Developer',
        'goal': 'Write complete XML External Entity scanner',
        'backstory': 'XML security expert'
    }
]

# Define corresponding tasks
task_configs = [
    {
        'description': 'Write a Python function to detect XSS vulnerabilities. Include error handling and multiple detection methods.',
        'expected_output': 'Complete XSS scanner function with error handling'
    },
    {
        'description': 'Write a Python function to detect SQL injection vulnerabilities. Include various SQLi techniques.',
        'expected_output': 'Complete SQL injection scanner function'
    },
    {
        'description': 'Write a Python function to detect CSRF vulnerabilities. Check for tokens and SameSite cookies.',
        'expected_output': 'Complete CSRF scanner function'
    },
    {
        'description': 'Write a Python function to detect directory traversal vulnerabilities. Test for path manipulation.',
        'expected_output': 'Complete path traversal scanner function'
    },
    {
        'description': 'Write a Python function to detect open redirect vulnerabilities. Check URL parameters.',
        'expected_output': 'Complete open redirect scanner function'
    },
    {
        'description': 'Write a Python function to detect XXE vulnerabilities. Test XML parsing issues.',
        'expected_output': 'Complete XXE scanner function'
    }
]

print("""
╔══════════════════════════════════════════════════════════════╗
║  🚀 MEMORY-EFFICIENT BATCHED PARALLEL EXECUTION              ║
║                                                              ║
║  Strategy: Batch 2 agents at a time, clean memory between   ║
║  Benefit: 2-3x faster than sequential, minimal RAM increase ║
║  Perfect for: 8GB RAM systems                                ║
╚══════════════════════════════════════════════════════════════╝
""")

# Create memory-efficient crew with batch size of 2
crew = MemoryEfficientCrew(
    model="ollama/qwen2.5:3b",
    batch_size=2  # 2 agents at a time
)

print("\n📋 Configuration:")
print(f"   Model: qwen2.5:3b")
print(f"   Total scanners to generate: {len(task_configs)}")
print(f"   Batch size: 2 (RAM-optimized)")
print(f"   Expected batches: 3")
print(f"\n⏳ This will take approximately 15-20 minutes...")

try:
    # Run batched execution
    results = crew.run_parallel_batches(agent_configs, task_configs)
    
    # Save results
    crew.save_results(results, output_dir="output/scanner_modules")
    
    print("\n" + "="*70)
    print("🎉 SUCCESS!")
    print("="*70)
    print(f"✅ Generated {len(results)} scanner modules")
    print(f"📁 Saved to: output/scanner_modules/")
    print("\nGenerated scanners:")
    for i, agent in enumerate(agent_configs, 1):
        print(f"  {i}. {agent['role']}")

except KeyboardInterrupt:
    print("\n\n⚠️  Interrupted by user")
    sys.exit(1)
except Exception as e:
    print(f"\n\n❌ Error: {e}")
    sys.exit(1)

