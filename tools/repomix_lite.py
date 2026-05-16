#!/usr/bin/env python3
"""
CHERENKOV Repomix-Lite: Consolidation tool for LLM context management.
Consolidates source code into a single Markdown file for RAG/Context optimization.
"""
import os
import argparse
from pathlib import Path

def build_repo_context(root_dir, output_file, ignore_dirs=None, extensions=None, include_files=None):
    """
    Crawls the repository and merges source files into a single Markdown document.
    """
    if ignore_dirs is None:
        ignore_dirs = {
            '.git', 'node_modules', '__pycache__', 'dist', 'build', 
            '.venv', 'venv', '.pytest_cache', '.ruff_cache', '.gemini',
            'agent_state', 'logs', 'output', 'workflow_results', 'workflow_checkpoints'
        }
    if extensions is None:
        # Focused on code, logic, and documentation
        extensions = {'.ts', '.py', '.js', '.json', '.md', '.yaml', '.yml', '.txt', '.sql', '.sh', '.ps1'}

    root_path = Path(root_dir).resolve()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# Repository Context: {root_path.name}\n")
        f.write("This file contains the codebase logic consolidated for LLM analysis.\n")
        f.write(f"Generated on: {os.popen('date /t').read().strip()} {os.popen('time /t').read().strip()}\n\n")

        for root, dirs, files in os.walk(root_path):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if d not in ignore_dirs]

            for file in files:
                file_path = Path(root) / file
                relative_path = file_path.relative_to(root_path)
                
                # Check extension and skip the output file itself
                if any(file.endswith(ext) for ext in extensions) and str(relative_path) != str(output_file):
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as code_file:
                            content = code_file.read()
                            
                        f.write(f"--- START OF FILE: {relative_path} ---\n")
                        f.write(f"```{file.split('.')[-1] if '.' in file else 'text'}\n")
                        f.write(content)
                        f.write("\n```\n")
                        f.write(f"--- END OF FILE: {relative_path} ---\n\n")
                        print(f"Added: {relative_path}")
                    except Exception as e:
                        print(f"Could not read {relative_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Consolidate repository into a single Markdown file.")
    parser.add_argument("--root", default=".", help="Root directory to crawl (default: current)")
    parser.add_argument("--output", default="repo_context_for_ai.md", help="Output file name")
    parser.add_argument("--ignore", help="Comma-separated list of directories to ignore")
    
    args = parser.parse_args()
    
    ignore_list = None
    if args.ignore:
        ignore_list = {i.strip() for i in args.ignore.split(",")}
        
    print(f"Consolidating repository at {os.path.abspath(args.root)}...")
    build_repo_context(args.root, args.output, ignore_dirs=ignore_list)
    print(f"\nSuccess! Consolidated context saved to: {args.output}")

if __name__ == "__main__":
    main()
