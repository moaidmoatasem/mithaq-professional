#!/usr/bin/env python3
"""
CHERENKOV — Runnable Multi-Agent Scan Simulation
Demonstrates the sovereign security analysis swarm workflow end-to-end.
Integrates directly with UnifiedLLMClient to execute sequential scanning jobs.
"""

import sys
from pathlib import Path

# Add src folder to sys.path so we can import easily
sys.path.append(str(Path(__file__).parent))
from vllm_client import UnifiedLLMClient, logger

# The target file to audit (simulated vulnerable script)
TARGET_CODE_TO_AUDIT = """
import os
import sqlite3
from flask import Flask, request

app = Flask(__name__)

# SECURITY ISSUE 1: Hardcoded credentials
DB_PASSWORD = "SovereignSecurityKey2026!#"

@app.route("/search")
def search_users():
    # SECURITY ISSUE 2: SQL Injection via string interpolation
    username = request.args.get("username", "")
    query = f"SELECT * FROM users WHERE name = '{username}'"
    
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    # SECURITY ISSUE 3: Shell execution vulnerability
    if username == "admin_backup":
        os.system(f"tar -czf /tmp/backup.tar.gz ./data/{username}")
        
    cursor.execute(query)
    return str(cursor.fetchall())
"""


class StaticAnalysisAgent:
    """Agent representing Cherenkov TENSOR static vulnerability scanner."""
    
    def __init__(self, client: UnifiedLLMClient):
        self.client = client
        self.role = "Vulnerability Scanner (TENSOR)"
        self.system_prompt = (
            "You are TENSOR, a sovereign static application security testing (SAST) agent. "
            "Your sole focus is identifying security flaws, CVE patterns, and insecure APIs in code. "
            "Provide detailed, technical findings. List file-level vulnerabilities clearly."
        )

    def scan(self, code: str) -> str:
        logger.info(f"Agent '{self.role}' beginning code vulnerability scan...")
        prompt = (
            "Analyze the following Python source code. List all security vulnerabilities you discover. "
            "For each finding, specify: \n"
            "1. Line / Area of vulnerability\n"
            "2. Vulnerability Type (e.g. SQL Injection, Hardcoded Secrets, Command Injection)\n"
            "3. Impact and risk severity (Critical/High/Medium/Low)\n\n"
            f"Code to analyze:\n```python\n{code}\n```"
        )
        return self.client.generate(
            prompt=prompt,
            system_prompt=self.system_prompt,
            temperature=0.1,  # Low temperature for highly deterministic/analytical results
            max_tokens=800
        )


class SecurityReportAgent:
    """Agent representing Cherenkov KINETIC triage and compliance reporting compiler."""
    
    def __init__(self, client: UnifiedLLMClient):
        self.client = client
        self.role = "Report Triage Compiler (KINETIC)"
        self.system_prompt = (
            "You are KINETIC, a sovereign compliance reporting agent. Your role is to take raw technical vulnerabilities, "
            "triage them, and compile a clean, structured Executive Security Report suitable for regulatory audits (e.g., SAMA/CBE)."
        )

    def compile_report(self, raw_findings: str) -> str:
        logger.info(f"Agent '{self.role}' aggregating raw scanner findings into executive compliance report...")
        prompt = (
            "Review the raw security scanner findings provided below. Triage them and compile a highly professional "
            "Executive Security Report. Include: \n"
            "1. Executive Summary table of findings (Vulnerability, Severity, Status)\n"
            "2. Categorized detailed recommendations for developers\n"
            "3. Clean, professional formatting.\n\n"
            f"Raw Findings:\n{raw_findings}"
        )
        return self.client.generate(
            prompt=prompt,
            system_prompt=self.system_prompt,
            temperature=0.3,
            max_tokens=1000
        )


def main():
    print("==========================================================")
    print("   CHERENKOV · SOVEREIGN SECURITY AGENT SWARM SIMULATOR   ")
    print("==========================================================\n")

    # 1. Parse CLI backend
    backend = "ollama"
    model = "qwen2.5-coder:7b"
    
    if len(sys.argv) > 1:
        backend = sys.argv[1].lower()
    if len(sys.argv) > 2:
        model = sys.argv[2]
        
    print(f"Backend set to: {backend.upper()} | Model: {model}")
    print("Initializing client layer...")
    
    try:
        client = UnifiedLLMClient(backend=backend, model_name=model)
    except Exception as e:
        logger.error(f"Failed to initialize unified client: {e}")
        sys.exit(1)

    # 2. Spawn Agents
    scanner = StaticAnalysisAgent(client)
    reporter = SecurityReportAgent(client)

    # 3. Step 1: Scan
    print("\n--- STEP 1: STATIC ANALYSIS SCANDING ---")
    try:
        raw_scan_results = scanner.scan(TARGET_CODE_TO_AUDIT)
        print("\n[Raw Scan Findings Output]:")
        print("----------------------------------------------------------")
        print(raw_scan_results)
        print("----------------------------------------------------------")
    except Exception as e:
        print(f"\n[!] Scanner failed during generation: {e}")
        print("    Ensure your backend server (Ollama or vLLM) is running and loaded.")
        sys.exit(1)

    # 4. Step 2: Compile Report
    print("\n--- STEP 2: TRIAGE & REPORT COMPILATION ---")
    try:
        final_report = reporter.compile_report(raw_scan_results)
        print("\n[Final Compliance Audit Report]:")
        print("==========================================================")
        print(final_report)
        print("==========================================================")
    except Exception as e:
        print(f"\n[!] Reporter compilation failed: {e}")
        sys.exit(1)

    # 5. Output Session Performance metrics
    print("\n==========================================================")
    print("   SESSION METRICS REPORT (AUDIT)")
    print("==========================================================")
    perf = client.get_performance_report()
    for k, v in perf.items():
        print(f"  {k:<25}: {v}")
    print("==========================================================\n")


if __name__ == "__main__":
    main()
