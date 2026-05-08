#!/usr/bin/env python3
"""
Test memory-efficient batched parallel execution
Generates 6 security scanners in 3 batches of 2
"""

import sys

from cherenkov.core.memory_efficient_parallel import MemoryEfficientCrew

# Define 6 different security scanner agents
agent_configs = [
    {
        "role": "XSS Scanner Developer",
        "goal": "Write complete XSS vulnerability scanner",
        "backstory": "Web security expert specializing in XSS detection",
    },
    {
        "role": "SQL Injection Scanner Developer",
        "goal": "Write complete SQL injection scanner",
        "backstory": "Database security expert with SQLi expertise",
    },
    {
        "role": "CSRF Scanner Developer",
        "goal": "Write complete CSRF vulnerability scanner",
        "backstory": "Web application security specialist",
    },
    {
        "role": "Directory Traversal Scanner Developer",
        "goal": "Write complete path traversal scanner",
        "backstory": "File system security expert",
    },
    {
        "role": "Open Redirect Scanner Developer",
        "goal": "Write complete open redirect scanner",
        "backstory": "URL security specialist",
    },
    {
        "role": "XXE Scanner Developer",
        "goal": "Write complete XML External Entity scanner",
        "backstory": "XML security expert",
    },
]

# Define corresponding tasks
task_configs = [
    {
        "description": "Write a Python function to detect XSS vulnerabilities. Include error handling and multiple detection methods.",
        "expected_output": "Complete XSS scanner function with error handling",
    },
    {
        "description": "Write a Python function to detect SQL injection vulnerabilities. Include various SQLi techniques.",
        "expected_output": "Complete SQL injection scanner function",
    },
    {
        "description": "Write a Python function to detect CSRF vulnerabilities. Check for tokens and SameSite cookies.",
        "expected_output": "Complete CSRF scanner function",
    },
    {
        "description": "Write a Python function to detect directory traversal vulnerabilities. Test for path manipulation.",
        "expected_output": "Complete path traversal scanner function",
    },
    {
        "description": "Write a Python function to detect open redirect vulnerabilities. Check URL parameters.",
        "expected_output": "Complete open redirect scanner function",
    },
    {
        "description": "Write a Python function to detect XXE vulnerabilities. Test XML parsing issues.",
        "expected_output": "Complete XXE scanner function",
    },
]

if __name__ == "__main__":
    crew = MemoryEfficientCrew(model="ollama/qwen2.5:3b", batch_size=2)

    try:
        results = crew.run_parallel_batches(agent_configs, task_configs)
        crew.save_results(results, output_dir="output/scanner_modules")
        print(f"Generated {len(results)} scanner modules → output/scanner_modules/")
    except KeyboardInterrupt:
        print("Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
