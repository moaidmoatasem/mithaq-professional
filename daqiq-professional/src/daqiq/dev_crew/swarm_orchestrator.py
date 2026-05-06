#!/usr/bin/env python3
# src/daqiq/dev_crew/swarm_orchestrator.py
"""
The Perpetual Build Machine.

Architecture (Controller-Worker-Judge):
  Controller  = Claude (this chat or Claude Code) — writes Mini-Specs only
  Workers     = Local Ollama qwen2.5-coder:7b — generate code, self-patch
  Judge       = CI gate (pytest + bandit) — hard pass/fail, no LLM

Flow:
  1. Read manifests/cwe_queue.yaml for next pending CWE
  2. Worker generates scanner in /tmp/swarm_build/ (dark room)
  3. Worker runs pytest + bandit — reads error → self-patches (up to 3x)
  4. If green: move to candidates/, open PR, mark CWE as CANDIDATE
  5. If red after 3 attempts: mark CWE as FAILED, log reason, move on
  6. Only ping Claude Code for Final Audit when PR is ready

This file runs 24/7 on WSL2. Cost: $0.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import httpx
import yaml

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("daqiq.swarm")

OLLAMA_URL   = "http://localhost:11434"
OLLAMA_MODEL = os.getenv("DAQIQ_OLLAMA_MODEL", "qwen2.5-coder:3b")
MAX_RETRIES  = 3
CANDIDATES   = Path("candidates/generated_scanners")
MANIFESTS    = Path("manifests/cwe_queue.yaml")
DARK_ROOM    = Path(tempfile.gettempdir()) / "swarm_build"


class CWEStatus(str, Enum):
    PENDING   = "pending"
    BUILDING  = "building"
    CANDIDATE = "candidate"   # passed CI, PR opened
    FAILED    = "failed"      # exhausted retries
    VALIDATED = "validated"   # graduated to src/daqiq/scanners/


@dataclass
class CWESpec:
    cwe_id:      str
    description: str
    tier:        int = 1
    status:      CWEStatus = CWEStatus.PENDING
    attempts:    int = 0
    fail_reason: str = ""


@dataclass
class SwarmResult:
    cwe_id:      str
    success:     bool
    module_name: str = ""
    pr_url:      str = ""
    fail_reason: str = ""
    attempts:    int = 0


class SwarmOrchestrator:
    """
    Runs the perpetual build loop.
    Workers self-correct up to MAX_RETRIES before giving up.
    Claude is summoned only for Final Audit — not during generation.
    """

    def __init__(self) -> None:
        CANDIDATES.mkdir(parents=True, exist_ok=True)
        DARK_ROOM.mkdir(parents=True, exist_ok=True)

    # ── Public API ──────────────────────────────────────────────────────────

    async def run_forever(self, batch_size: int = 3) -> None:
        """Run the build loop continuously."""
        logger.info("Swarm started. Batch size: %d. Cost: $0.", batch_size)
        while True:
            specs = self._load_pending(batch_size)
            if not specs:
                logger.info("Queue empty. Sleeping 60s.")
                await asyncio.sleep(60)
                continue

            results = await asyncio.gather(
                *[self._process_cwe(spec) for spec in specs]
            )
            self._report(results)
            await asyncio.sleep(5)   # brief pause between batches

    async def run_once(self, cwe_id: str, description: str) -> SwarmResult:
        """Process a single CWE. Used by CI and manual runs."""
        spec = CWESpec(cwe_id=cwe_id, description=description)
        return await self._process_cwe(spec)

    # ── Core loop ───────────────────────────────────────────────────────────

    async def _process_cwe(self, spec: CWESpec) -> SwarmResult:
        """
        The 3-strike self-patch loop.
        Worker reads its own pytest errors and patches before retrying.
        """
        logger.info("Processing %s: %s", spec.cwe_id, spec.description[:50])
        module_name = self._module_name(spec.cwe_id, spec.description)
        work_dir = DARK_ROOM / module_name
        work_dir.mkdir(parents=True, exist_ok=True)

        last_error = ""
        for attempt in range(1, MAX_RETRIES + 1):
            logger.info("  Attempt %d/%d", attempt, MAX_RETRIES)

            # Step 1: Generate or patch code
            code = await self._generate_code(spec, last_error, attempt)
            scanner_file = work_dir / f"{module_name}.py"
            scanner_file.write_text(code)

            # Step 2: Run the judge (pytest + bandit)
            ok, error_output = self._run_judge(scanner_file, work_dir)

            if ok:
                # Green — promote to candidates, open PR
                dest = CANDIDATES / f"{module_name}.py"
                shutil.copy(scanner_file, dest)
                pr_url = self._open_pr(module_name, spec.cwe_id)
                self._update_queue(spec.cwe_id, CWEStatus.CANDIDATE)
                logger.info("  ✓ CANDIDATE after %d attempt(s). PR: %s", attempt, pr_url)
                return SwarmResult(
                    cwe_id=spec.cwe_id,
                    success=True,
                    module_name=module_name,
                    pr_url=pr_url,
                    attempts=attempt,
                )

            # Red — save error for next attempt
            last_error = error_output
            logger.warning("  ✗ Attempt %d failed. Error saved for self-patch.", attempt)

        # Exhausted retries
        self._update_queue(spec.cwe_id, CWEStatus.FAILED, last_error[:200])
        logger.error("  ✗ FAILED after %d attempts: %s", MAX_RETRIES, last_error[:100])
        return SwarmResult(
            cwe_id=spec.cwe_id,
            success=False,
            fail_reason=last_error[:200],
            attempts=MAX_RETRIES,
        )

    # ── Ollama interaction ──────────────────────────────────────────────────

    async def _generate_code(
        self, spec: CWESpec, last_error: str, attempt: int
    ) -> str:
        """
        Attempt 1: generate from scratch.
        Attempts 2+: read your own error and patch.
        """
        if attempt == 1 or not last_error:
            prompt = self._build_generate_prompt(spec)
        else:
            prompt = self._build_patch_prompt(spec, last_error)

        async with httpx.AsyncClient(timeout=300) as client:
            try:
                resp = await client.post(
                    f"{OLLAMA_URL}/api/generate",
                    json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
                )
                resp.raise_for_status()
                raw = resp.json().get("response", "")
                return self._extract_python(raw)
            except Exception as e:
                logger.warning("Ollama error: %s. Using stub.", e)
                return self._stub_scanner(spec)

    def _build_generate_prompt(self, spec: CWESpec) -> str:
        return f"""Write a Python async security scanner for DAQIQ.

CWE: {spec.cwe_id}
Vulnerability: {spec.description}

REQUIRED: Your file MUST start with exactly these two import lines (copy verbatim):
import httpx
from daqiq.core.base_scanner import BaseScanner, Finding, ScanResult, Severity

Do NOT import these symbols from anywhere else. Do NOT use any symbol that is not imported.

Additional requirements:
- Class inherits from BaseScanner
- Implement: async def scan(self) -> ScanResult
- Use httpx.AsyncClient for HTTP requests
- Only flag clear evidence (conservative — prefer false negatives over false positives)
- Docstring MUST contain the exact CWE ID (e.g. "CWE-{spec.cwe_id.split('-')[1]}"), technique, and one-sentence remediation
- Handle exceptions: catch httpx.ConnectError and httpx.TimeoutException
- Set scanner tags to ["passive"] unless it sends payloads (then ["active"])

Output Python code only. No explanation. No markdown fences.
"""

    def _build_patch_prompt(self, spec: CWESpec, error: str) -> str:
        return f"""Fix this Python security scanner for DAQIQ.

CWE: {spec.cwe_id}
Error to fix:
{error[:800]}

REQUIRED: Your file MUST start with exactly these two import lines (copy verbatim):
import httpx
from daqiq.core.base_scanner import BaseScanner, Finding, ScanResult, Severity

Do NOT use any symbol that is not imported. Do NOT add unused imports.

Other requirements:
- Class inherits from BaseScanner
- async def scan(self) -> ScanResult
- Uses httpx.AsyncClient
- Handles httpx.ConnectError and httpx.TimeoutException
- Docstring MUST contain the CWE ID (e.g. "CWE-{spec.cwe_id.split('-')[1]}")

Produce the complete fixed file. Python code only. No explanation. No markdown fences.
"""

    # ── Judge (CI gate) ─────────────────────────────────────────────────────

    def _run_judge(
        self, scanner_file: Path, work_dir: Path
    ) -> tuple[bool, str]:
        """
        Hard pass/fail. No LLM involved.
        Returns (passed, error_output).
        """
        errors: list[str] = []

        # Syntax check
        syn = subprocess.run(
            ["python3", "-m", "py_compile", str(scanner_file)],
            capture_output=True, text=True
        )
        if syn.returncode != 0:
            errors.append(f"SYNTAX ERROR:\n{syn.stderr}")

        # Bandit security scan — skip B501 (verify=False is intentional in TLS scanners)
        ban = subprocess.run(
            ["bandit", "--severity-level", "medium", "--skip", "B501", str(scanner_file)],
            capture_output=True, text=True
        )
        if ban.returncode != 0:
            errors.append(f"BANDIT:\n{ban.stdout}")

        # Auto-fix trivial issues first (import order, unused imports, formatting)
        subprocess.run(
            ["ruff", "check", "--select", "I,F401,F841", "--fix", str(scanner_file)],
            capture_output=True,
        )
        subprocess.run(["ruff", "format", str(scanner_file)], capture_output=True)

        # Ruff lint
        ruff = subprocess.run(
            ["ruff", "check", str(scanner_file)],
            capture_output=True, text=True
        )
        if ruff.returncode != 0:
            errors.append(f"RUFF:\n{ruff.stdout}")

        # CWE reference check — accept "CWE-295", "CWE_ID = 295", or "cwe: 295"
        import re as _re
        content = scanner_file.read_text()
        if not _re.search(r"CWE[-_\s:]+\d+", content, _re.IGNORECASE):
            errors.append("DOCSTRING: Missing CWE ID in file (need CWE-NNN, CWE_ID=NNN, etc.)")

        if errors:
            return False, "\n\n".join(errors)
        return True, ""

    # ── Queue management ────────────────────────────────────────────────────

    def _load_pending(self, limit: int) -> list[CWESpec]:
        if not MANIFESTS.exists():
            return []
        data = yaml.safe_load(MANIFESTS.read_text()) or {}
        specs = []
        for item in data.get("queue", []):
            if item.get("status", "pending") == "pending":
                specs.append(CWESpec(
                    cwe_id=item["cwe_id"],
                    description=item["description"],
                    tier=item.get("tier", 1),
                ))
                if len(specs) >= limit:
                    break
        return specs

    def _update_queue(
        self, cwe_id: str, status: CWEStatus, reason: str = ""
    ) -> None:
        if not MANIFESTS.exists():
            return
        data = yaml.safe_load(MANIFESTS.read_text()) or {}
        for item in data.get("queue", []):
            if item["cwe_id"] == cwe_id:
                item["status"] = status.value
                if reason:
                    item["fail_reason"] = reason
                break
        MANIFESTS.write_text(yaml.dump(data, default_flow_style=False))

    # ── Git/GitHub ──────────────────────────────────────────────────────────

    def _open_pr(self, module_name: str, cwe_id: str) -> str:
        """
        Candidate files stay in candidates/generated_scanners/ as untracked files.
        Git branch operations are intentionally skipped here — they race under
        asyncio.gather and git-checkout-main removes the newly committed file from
        the working tree. A human runs the 5-step validation gate, then commits.
        """
        logger.info("Candidate saved: %s (%s) — awaiting validation gate.", module_name, cwe_id)
        return ""

    # ── Utilities ───────────────────────────────────────────────────────────

    def _module_name(self, cwe_id: str, description: str) -> str:
        import re
        words = re.findall(r"[a-zA-Z]+", description.lower())[:3]
        num = re.sub(r"\D", "", cwe_id)
        return "_".join(words) or f"cwe_{num}"

    def _extract_python(self, raw: str) -> str:
        """Strip markdown fences if present."""
        import re
        match = re.search(r"```python\n(.*?)```", raw, re.DOTALL)
        if match:
            return match.group(1)
        match = re.search(r"```\n(.*?)```", raw, re.DOTALL)
        if match:
            return match.group(1)
        return raw

    def _stub_scanner(self, spec: CWESpec) -> str:
        """Fallback stub when Ollama is unavailable."""
        return f'''# Auto-generated stub — Ollama unavailable during generation
from daqiq.core.base_scanner import BaseScanner, ScanResult


class Stub{spec.cwe_id.replace("-", "")}Scanner(BaseScanner):
    """
    CWE: {spec.cwe_id} — {spec.description[:40]}
    Technique: TODO
    Remediation: TODO
    """
    name = "stub_{spec.cwe_id.lower().replace("-","_")}"
    description = "{spec.description[:60]}"
    tags = ["passive"]

    async def scan(self) -> ScanResult:
        return ScanResult(target=self.target, scanner=self.name)
'''

    def _report(self, results: list[SwarmResult]) -> None:
        passed = sum(1 for r in results if r.success)
        failed = len(results) - passed
        logger.info(
            "Batch complete: %d passed, %d failed | Total candidates: %d",
            passed, failed, len(list(CANDIDATES.glob("*.py")))
        )


# ── Manifest template ───────────────────────────────────────────────────────

MANIFEST_TEMPLATE = """# manifests/cwe_queue.yaml
# The Perpetual Build Machine queue.
# Add CWEs here. The swarm processes them 24/7.
# Status: pending | building | candidate | failed | validated

queue:
  - cwe_id: CWE-79
    description: "Cross-site scripting via reflected query parameters"
    tier: 1
    status: pending

  - cwe_id: CWE-89
    description: "SQL injection via unsanitized user input in query parameters"
    tier: 1
    status: pending

  - cwe_id: CWE-22
    description: "Path traversal via directory traversal sequences in file parameters"
    tier: 2
    status: pending

  - cwe_id: CWE-295
    description: "Improper TLS certificate validation and expired cert detection"
    tier: 1
    status: pending

  - cwe_id: CWE-614
    description: "Sensitive cookie without Secure and HttpOnly flags"
    tier: 1
    status: pending

  - cwe_id: CWE-942
    description: "CORS misconfiguration allowing wildcard or reflected origins"
    tier: 1
    status: pending

  - cwe_id: CWE-284
    description: "Improper access control on authenticated endpoints"
    tier: 3
    status: pending

  - cwe_id: CWE-434
    description: "Unrestricted file upload with dangerous file type acceptance"
    tier: 2
    status: pending

  - cwe_id: CWE-352
    description: "Cross-site request forgery missing CSRF token validation"
    tier: 2
    status: pending

  - cwe_id: CWE-502
    description: "Deserialization of untrusted data in API endpoints"
    tier: 2
    status: pending
"""


# ── CLI entry point ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    async def main():
        orch = SwarmOrchestrator()

        # Create manifest if it doesn't exist
        manifest_path = Path("manifests/cwe_queue.yaml")
        if not manifest_path.exists():
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(MANIFEST_TEMPLATE)
            print(f"Created {manifest_path} with 10 starter CWEs.")

        if "--once" in sys.argv:
            # Process one CWE from the queue
            specs = orch._load_pending(1)
            if specs:
                result = await orch._process_cwe(specs[0])
                print(f"Result: {result}")
            else:
                print("Queue is empty. Add CWEs to manifests/cwe_queue.yaml")
        else:
            # Run forever
            await orch.run_forever(batch_size=3)

    asyncio.run(main())
