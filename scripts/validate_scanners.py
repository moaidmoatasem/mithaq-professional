#!/usr/bin/env python3
"""
CHERENKOV — AI-Generated Scanner Evaluation & Validation Pipeline
Provides automated assessment of generated security scanner code to verify:
  1. Valid Python syntax (AST validation)
  2. Compliance with core Scanner interfaces
  3. Accuracy rates (True Positive vs False Positive) against benchmark cases
"""

import os
import sys
import ast
import importlib.util
import logging
from typing import Dict, Any, List

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(name)s) %(message)s"
)
logger = logging.getLogger("CherenkovScannerValidator")

# ── Benchmark Evaluation Cases ───────────────────────────────────────────────
BENCHMARK_CASES = [
    # True Positives (Vulnerable snippets that should be matched)
    {
        "id": "TP_SQLI",
        "label": "Vulnerable SQL Query",
        "is_vulnerable": True,
        "code": "query = f'SELECT * FROM users WHERE username = \"{user_input}\"'\ncursor.execute(query)"
    },
    {
        "id": "TP_RCE",
        "label": "Vulnerable System Execution",
        "is_vulnerable": True,
        "code": "import os\nos.system('tar -czf backup.tar.gz ' + folder_path)"
    },
    # False Positives (Safe code snippets that should NOT be flagged as vulnerable)
    {
        "id": "FP_SAFE_SQL",
        "label": "Parameterized SQL Query",
        "is_vulnerable": False,
        "code": "cursor.execute('SELECT * FROM users WHERE username = ?', (user_input,))"
    },
    {
        "id": "FP_SAFE_SHELL",
        "label": "Safe Subprocess Call",
        "is_vulnerable": False,
        "code": "import subprocess\nsubprocess.run(['tar', '-czf', 'backup.tar.gz', folder_path], check=True)"
    }
]


class ScannerValidator:
    """Automated QA validator for newly generated scanning modules."""

    def __init__(self, scanner_file_path: str):
        self.file_path = scanner_file_path
        self.module_name = os.path.splitext(os.path.basename(scanner_file_path))[0]

    def check_syntax(self) -> bool:
        """Validates that the file contains syntactically correct Python code using AST."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                source = f.read()
            ast.parse(source)
            logger.info("  [PASS] Syntax check successful (Valid AST).")
            return True
        except SyntaxError as e:
            logger.error(f"  [FAIL] Syntax check failed: {e.msg} on line {e.lineno}")
            return False
        except Exception as e:
            logger.error(f"  [FAIL] Failed to read scanner file: {e}")
            return False

    def load_scanner_class(self) -> Any:
        """Dynamically imports the scanner module and retrieves the class definition."""
        try:
            spec = importlib.util.spec_from_file_location(self.module_name, self.file_path)
            if not spec or not spec.loader:
                logger.error("  [FAIL] Failed to construct spec loader.")
                return None
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[self.module_name] = module
            spec.loader.exec_module(module)
            
            # Look for a class inheriting from a scanner structure or having a scan function
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and attr_name != "BaseScanner":
                    # Check if it has a scan method
                    if hasattr(attr, "scan") and callable(getattr(attr, "scan")):
                        logger.info(f"  [PASS] Found compliant scanner class: {attr_name}")
                        return attr
                        
            logger.error("  [FAIL] No compliant scanner class with a 'scan()' method was found in the module.")
            return None
        except Exception as e:
            logger.error(f"  [FAIL] Failed to dynamically load module: {e}")
            return None

    def evaluate_performance(self, scanner_class: Any) -> Dict[str, Any]:
        """Runs the scanner class against our security benchmarks to measure accuracy."""
        logger.info("Beginning vulnerability detection performance evaluation...")
        
        true_positives = 0
        false_positives = 0
        total_tp_cases = sum(1 for c in BENCHMARK_CASES if c["is_vulnerable"])
        total_fp_cases = sum(1 for c in BENCHMARK_CASES if not c["is_vulnerable"])
        
        # Instantiate scanner
        try:
            scanner_instance = scanner_class()
        except Exception as e:
            logger.error(f"  [FAIL] Failed to instantiate scanner class: {e}")
            return {"status": "Instantiation Error", "details": str(e)}

        results = []
        for case in BENCHMARK_CASES:
            try:
                # Execute scan
                findings = scanner_instance.scan(case["code"])
                has_findings = len(findings) > 0 if isinstance(findings, (list, str)) else bool(findings)
                
                # Check outcome matches label
                if case["is_vulnerable"] and has_findings:
                    true_positives += 1
                    status = "CORRECT (Vulnerability Identified)"
                elif not case["is_vulnerable"] and not has_findings:
                    status = "CORRECT (Safe Code Ignored)"
                elif not case["is_vulnerable"] and has_findings:
                    false_positives += 1
                    status = "INCORRECT (False Positive Triggered)"
                else:
                    status = "INCORRECT (Vulnerability Missed)"
                    
                results.append({
                    "case_id": case["id"],
                    "label": case["label"],
                    "is_vulnerable": case["is_vulnerable"],
                    "scan_outcome_flagged": has_findings,
                    "status": status
                })
            except Exception as e:
                logger.warning(f"Error evaluating test case {case['id']}: {e}")
                results.append({
                    "case_id": case["id"],
                    "status": f"Evaluation Error: {e}"
                })

        tp_rate = (true_positives / total_tp_cases) * 100 if total_tp_cases > 0 else 0
        fp_rate = (false_positives / total_fp_cases) * 100 if total_fp_cases > 0 else 0
        
        return {
            "status": "Success",
            "true_positive_rate": f"{tp_rate:.1f}%",
            "false_positive_rate": f"{fp_rate:.1f}%",
            "cases_evaluated": len(BENCHMARK_CASES),
            "results": results
        }


if __name__ == "__main__":
    print("==========================================================")
    print("     CHERENKOV · SECURITY SCANNER AUTONOMIC VALIDATOR     ")
    print("==========================================================\n")
    
    # Create a mock scanner file for self-validation
    mock_scanner_code = """
class AutonomicSQLScanner:
    def __init__(self):
        self.name = "AutonomicSQLScanner"

    def scan(self, code: str) -> list:
        findings = []
        # Basic heuristic mapping to simulate detection
        if "f'SELECT" in code or "os.system" in code:
            findings.append({
                "vulnerability": "Code Injection Pattern",
                "severity": "High"
            })
        return findings
"""
    mock_file = "temp_mock_scanner.py"
    with open(mock_file, "w", encoding="utf-8") as f:
        f.write(mock_scanner_code)

    try:
        validator = ScannerValidator(mock_file)
        print(f"Step 1: Check syntax for {mock_file}...")
        if validator.check_syntax():
            print("\nStep 2: Dynamic class inspection...")
            scanner_class = validator.load_scanner_class()
            if scanner_class:
                print("\nStep 3: Accuracy evaluation...")
                metrics = validator.evaluate_performance(scanner_class)
                print("\n================ EVALUATION METRICS ================")
                for key, val in metrics.items():
                    if key != "results":
                        print(f"  {key:<22}: {val}")
                print("----------------------------------------------------")
                for res in metrics["results"]:
                    print(f"  Case: {res['case_id']:<12} | Status: {res['status']}")
                print("====================================================\n")
    finally:
        if os.path.exists(mock_file):
            os.remove(mock_file)
