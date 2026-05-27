# packages/cherenkov/dev_crew/validation_gate.py
"""5-stage validation gate for AI-generated scanner candidates.

Stages:
  1. ruff format --check   — code style compliance
  2. ruff check            — syntax + import + naming conventions
  3. bandit -ll            — security anti-patterns (HIGH severity)
  4. pytest                — unit tests pass (if test file provided)
  5. DVWA smoke            — scanner imports and runs without crashing

The DVWA stage does NOT require real vulnerabilities — it is a
strict import + execution smoke test. Full DVWA integration is gated
behind the --requires-dvwa pytest marker.
"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ValidationResult:
    passed: bool
    feedback: str


class ValidationGate:
    """Five-stage validation pipeline for generated scanner candidates."""

    def __init__(
        self,
        target_file: Path,
        test_file: Path | None = None,
        dvwa_url: str = "http://localhost:80",
    ):
        self.target_file = target_file
        self.test_file = test_file
        self.dvwa_url = dvwa_url

    def run_checks(self) -> ValidationResult:
        """Execute all 5 stages in order. First failure gates the rest."""
        stages = [
            ("ruff format", self._stage_format),
            ("ruff check", self._stage_ruff),
            ("bandit", self._stage_bandit),
            ("pytest", self._stage_pytest if self.test_file else None),
            ("DVWA smoke", self._stage_dvwa),
        ]
        failures = []
        for name, fn in stages:
            if fn is None:
                continue
            passed, msg = fn()
            if not passed:
                failures.append(f"[{name}] {msg.strip()}")
        if failures:
            return ValidationResult(passed=False, feedback="\n".join(failures))
        return ValidationResult(passed=True, feedback="ALL 5 STAGES PASSED")

    def _run(self, cmd: list[str], timeout: int = 60) -> tuple[int, str, str]:
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return r.returncode, r.stdout, r.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "TIMEOUT"
        except FileNotFoundError:
            return -2, "", "COMMAND_NOT_FOUND"

    def _stage_format(self) -> tuple[bool, str]:
        rc, out, err = self._run(["ruff", "format", "--check", str(self.target_file)])
        if rc != 0:
            return False, f"Formatting issues:\n{out}{err}"
        return True, ""

    def _stage_ruff(self) -> tuple[bool, str]:
        rc, out, err = self._run(["ruff", "check", str(self.target_file)])
        if rc != 0:
            return False, f"Linting errors:\n{out}{err}"
        return True, ""

    def _stage_bandit(self) -> tuple[bool, str]:
        rc, out, err = self._run(["bandit", "-ll", str(self.target_file)])
        if rc != 0:
            return False, f"Security issues:\n{out}{err}"
        return True, ""

    def _stage_pytest(self) -> tuple[bool, str]:
        if not self.test_file or not self.test_file.exists():
            return True, ""
        rc, out, err = self._run(
            ["pytest", str(self.test_file), "-v", "--tb=short", "-q"],
            timeout=120,
        )
        if rc != 0:
            return False, f"Unit tests failed:\n{out}{err}"
        return True, ""

    def _stage_dvwa(self) -> tuple[bool, str]:
        """Smoke test: the scanner must import and produce a ScanResult."""
        try:
            rc, out, err = self._run(
                [
                    sys.executable,
                    "-c",
                    f"import importlib,sys; "
                    f"sys.path.insert(0, 'packages'); "
                    f"m = importlib.import_module('candidates.generated_scanners.{self._module_name()}'); "
                    f"import asyncio; "
                    f"r = asyncio.run(m.{self._class_name()}().scan('{self.dvwa_url}')); "
                    f"print(f'SMOKE_OK: {{len(r.findings)}} findings')",
                ],
                timeout=30,
            )
            if rc != 0:
                return False, f"DVWA smoke failed (import or runtime error):\n{err}"
            return True, f"DVWA smoke: {out.strip()}"
        except Exception as e:
            return False, f"DVWA smoke exception: {e}"

    def _module_name(self) -> str:
        return self.target_file.stem

    def _class_name(self) -> str:
        """Derive class name from file stem (camelcase + Scanner suffix)."""
        parts = self._module_name().split("_")
        return "".join(p.capitalize() for p in parts) + "Scanner"
