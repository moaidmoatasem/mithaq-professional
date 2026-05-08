# src/mithaq/dev_crew/scanner_generator.py
"""
Scanner template generator.
(Accepted: Gemini — accelerates Phase 3, makes 50 scanners in 10 weeks viable)

Uses qwen2.5-coder:7b locally. Cost: $0.
Input: CWE ID + vulnerability description
Output: BaseScanner implementation + positive/negative test stubs + DVWA harness

This tool NEVER writes directly to src/mithaq/scanners/.
Output always goes to candidates/generated_scanners/.
Validation gate enforced separately.
"""
from __future__ import annotations

import re
import textwrap
from pathlib import Path
from typing import NamedTuple

import httpx

OLLAMA_URL   = "http://localhost:11434"
OLLAMA_MODEL = "qwen2.5-coder:7b"

CANDIDATES_DIR = Path("candidates/generated_scanners")

SCANNER_TEMPLATE = """
# candidates/generated_scanners/{module_name}.py
# GENERATED — not validated. Run validation gate before promoting.
# CWE: {cwe_id}
# Generated from: {description_snippet}
from __future__ import annotations

import httpx

from mithaq.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class {class_name}(BaseScanner):
    \"\"\"
    CWE: {cwe_id} — {cwe_name}
    Technique: [TODO — describe what requests are made]
    Remediation: [TODO — one-sentence fix]

    Validation gate status: PENDING
    \"\"\"

    name        = "{scanner_name}"
    description = "{description_snippet}"
    tags        = {tags}

    async def scan(self) -> ScanResult:
        result = ScanResult(target=self.target, scanner=self.name)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(self.target)

            # TODO: implement detection logic
            # finding = self.finding(
            #     title="{cwe_name} detected",
            #     severity=Severity.MEDIUM,
            #     description="[TODO]",
            #     evidence="[TODO]",
            #     remediation="[TODO]",
            #     cwe_id="{cwe_id}",
            # )
            # result.findings.append(finding)

        except (httpx.ConnectError, httpx.TimeoutException) as e:
            result.error = str(e)

        return result
""".lstrip()

TEST_TEMPLATE = """
# tests/unit/scanners/test_{module_name}.py
# GENERATED — not validated.
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from mithaq.scanners.{module_name} import {class_name}
from mithaq.core.base_scanner import Severity


@pytest.mark.asyncio
async def test_{module_name}_positive():
    \"\"\"Must fire when vulnerability present (mocked HTTP).\"\"\"
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock:
        # TODO: configure mock to return vulnerable response
        mock.return_value = MagicMock(
            headers={{}},
            status_code=200,
            text="TODO: vulnerable response body",
        )
        result = await {class_name}("https://example.com").scan()
    # TODO: assert findings present with correct severity
    # assert len(result.findings) >= 1
    # assert result.findings[0].severity == Severity.MEDIUM
    assert result is not None  # placeholder until TODO is filled


@pytest.mark.asyncio
async def test_{module_name}_negative():
    \"\"\"Must NOT fire when vulnerability absent (false-positive check).\"\"\"
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock:
        # Safe response - no vulnerability detected
        mock.return_value = MagicMock(
            headers={{}},
            status_code=200,
            text="<html><body>Safe Content - No Vulnerability Found</body></html>",
        )
        result = await {class_name}("https://example.com").scan()
    assert result.findings == [], f"False positive: {{result.findings}}"


@pytest.mark.asyncio
@pytest.mark.requires_dvwa
async def test_{module_name}_dvwa():
    \"\"\"Integration: must find known vulnerability on DVWA.\"\"\"
    result = await {class_name}("http://localhost:8080").scan()
    assert len(result.findings) > 0, (
        "Expected to find {cwe_name} on DVWA but got no findings. "
        "Check DVWA is running: docker run -d -p 8080:80 vulnerables/web-dvwa"
    )
""".lstrip()


class GeneratedScanner(NamedTuple):
    module_name:   str
    class_name:    str
    scanner_file:  str
    test_file:     str
    cwe_id:        str


class ScannerGenerator:
    """
    Dev crew tool: generates scanner candidates from CVE/CWE descriptions.

    Usage:
        gen = ScannerGenerator()
        result = await gen.generate("CWE-79", "Cross-site scripting via query params")
        # Writes to candidates/generated_scanners/
        # Run validation gate separately
    """

    async def generate(self, cwe_id: str, description: str) -> GeneratedScanner:
        # Step 1: Ask Ollama to fill in the detection logic
        detection_logic = await self._ask_ollama(cwe_id, description)

        # Step 2: Derive naming
        module_name, class_name, scanner_name, tags = self._derive_names(cwe_id, description)

        # Step 3: Build the scanner file
        cwe_name = self._cwe_name(cwe_id)
        desc_snippet = description[:60].rstrip()

        scanner_code = SCANNER_TEMPLATE.format(
            module_name=module_name,
            class_name=class_name,
            scanner_name=scanner_name,
            cwe_id=cwe_id,
            cwe_name=cwe_name,
            description_snippet=desc_snippet,
            tags=repr(tags),
        )

        # Inject Ollama-generated detection logic if usable
        if detection_logic and len(detection_logic) > 50:
            scanner_code = scanner_code.replace(
                "            # TODO: implement detection logic",
                "            # Generated by qwen2.5-coder:7b — VERIFY before use\n"
                + textwrap.indent(detection_logic, "            ")
            )

        # Step 4: Build the test file
        test_code = TEST_TEMPLATE.format(
            module_name=module_name,
            class_name=class_name,
            cwe_id=cwe_id,
            cwe_name=cwe_name,
        )

        # Step 5: Write files
        CANDIDATES_DIR.mkdir(parents=True, exist_ok=True)
        scanner_path = CANDIDATES_DIR / f"{module_name}.py"
        test_dir = Path("tests/unit/scanners")
        test_dir.mkdir(parents=True, exist_ok=True)
        test_path = test_dir / f"test_{module_name}.py"

        scanner_path.write_text(scanner_code)
        test_path.write_text(test_code)

        return GeneratedScanner(
            module_name=module_name,
            class_name=class_name,
            scanner_file=str(scanner_path),
            test_file=str(test_path),
            cwe_id=cwe_id,
        )

    async def _ask_ollama(self, cwe_id: str, description: str) -> str:
        """Ask local Ollama to generate detection logic for the scanner."""
        prompt = (
            f"Write ONLY the detection logic body for a Python async security scanner.\n"
            f"CWE: {cwe_id}. Vulnerability: {description}.\n"
            f"Use httpx.AsyncClient. Append Finding objects to result.findings.\n"
            f"Be conservative: only flag clear evidence. No speculative findings.\n"
            f"Output Python code only, no explanation, no imports.\n"
        )
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(
                    f"{OLLAMA_URL}/api/generate",
                    json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
                )
                resp.raise_for_status()
                return resp.json().get("response", "")
        except Exception as e:
            return f"# Ollama unavailable: {e}"

    def _derive_names(
        self, cwe_id: str, description: str
    ) -> tuple[str, str, str, list[str]]:
        cwe_num = re.sub(r"\D", "", cwe_id)
        words = re.findall(r"[a-zA-Z]+", description.lower())[:4]
        module_name  = "_".join(words) or f"cwe_{cwe_num}"
        class_name   = "".join(w.capitalize() for w in words) + "Scanner"
        scanner_name = "_".join(words)
        tags = ["passive"]
        if any(w in description.lower() for w in ["inject", "traversal", "bypass", "attack"]):
            tags = ["active"]
        return module_name, class_name, scanner_name, tags

    def _cwe_name(self, cwe_id: str) -> str:
        names = {
            "CWE-79":  "Cross-site Scripting (XSS)",
            "CWE-89":  "SQL Injection",
            "CWE-22":  "Path Traversal",
            "CWE-284": "Improper Access Control",
            "CWE-287": "Improper Authentication",
            "CWE-295": "Improper Certificate Validation",
            "CWE-326": "Inadequate Encryption Strength",
            "CWE-352": "Cross-Site Request Forgery",
            "CWE-434": "Unrestricted File Upload",
            "CWE-502": "Deserialization of Untrusted Data",
            "CWE-614": "Sensitive Cookie Without Secure Flag",
            "CWE-942": "CORS Misconfiguration",
        }
        return names.get(cwe_id, cwe_id)

