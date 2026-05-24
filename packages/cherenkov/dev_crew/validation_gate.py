import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ValidationResult:
    passed: bool
    feedback: str


class ValidationGate:
    def __init__(self, target_file: Path, test_file: Path | None = None):
        self.target_file = target_file
        self.test_file = test_file

    def run_checks(self) -> ValidationResult:
        """Runs ruff lint, ruff format, and optional pytest on the generated file."""
        lint = subprocess.run(
            ["ruff", "check", str(self.target_file)],
            capture_output=True,
            text=True,
        )
        if lint.returncode != 0:
            return ValidationResult(
                passed=False,
                feedback=f"LINTING FAILED. Fix these errors:\n{lint.stdout}",
            )

        subprocess.run(["ruff", "format", str(self.target_file)], capture_output=True)

        if self.test_file and self.test_file.exists():
            tests = subprocess.run(
                ["pytest", str(self.test_file), "-v", "--tb=short"],
                capture_output=True,
                text=True,
            )
            if tests.returncode != 0:
                return ValidationResult(
                    passed=False,
                    feedback=f"UNIT TESTS FAILED:\n{tests.stdout}",
                )

        return ValidationResult(passed=True, feedback="ALL CHECKS PASSED.")
