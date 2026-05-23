# packages/cherenkov/dev_crew/validation_gate.py
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ValidationResult:
    passed: bool
    feedback: str

class ValidationGate:
    def __init__(self, target_file: Path, test_file: Path = None):
        self.target_file = target_file
        self.test_file = test_file

    def run_checks(self) -> ValidationResult:
        """Runs strict deterministic checks on the generated code."""

        # 1. Syntax and Linting Check (Ruff)
        lint_result = subprocess.run(
            ["ruff", "check", str(self.target_file)],
            capture_output=True, text=True
        )
        if lint_result.returncode != 0:
            return ValidationResult(
                passed=False,
                feedback=f"LINTING FAILED. Fix these errors:\n{lint_result.stdout}"
            )

        # 2. Formatting Check (Ruff format)
        subprocess.run(["ruff", "format", str(self.target_file)], capture_output=True)

        # 3. Unit Testing Check (Pytest) - Only if a test file is provided
        if self.test_file and self.test_file.exists():
            test_result = subprocess.run(
                ["pytest", str(self.test_file), "-v", "--tb=short"],
                capture_output=True, text=True
            )
            if test_result.returncode != 0:
                return ValidationResult(
                    passed=False,
                    feedback=f"UNIT TESTS FAILED. Output:\n{test_result.stdout}"
                )

        return ValidationResult(passed=True, feedback="ALL CHECKS PASSED. Code is compliant.")
