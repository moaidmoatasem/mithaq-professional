"""NucleiScanner — wraps nuclei for active vulnerability scanning"""

import asyncio
import json
import logging
from datetime import datetime
from typing import List

from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity

logger = logging.getLogger(__name__)


class NucleiScanner(BaseScanner):
    name = "nuclei_scanner"
    description = "Runs nuclei -severity critical,high against target"
    tags = ["active", "nuclei", "third_party"]

    def __init__(self, name: str = "", description: str = ""):
        super().__init__(name or self.name, description or self.description)

    async def scan(self, target: str, timeout: float = 120.0) -> ScanResult:
        start = datetime.now()
        findings: List[Finding] = []

        cmd = [
            "nuclei",
            "-u",
            target,
            "-severity",
            "critical,high",
            "-json",
            "-timeout",
            str(int(timeout)),
        ]

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)

            if proc.returncode != 0:
                logger.warning(
                    "nuclei exited with code %d: %s",
                    proc.returncode,
                    stderr.decode(errors="replace"),
                )

            for line in stdout.decode(errors="replace").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue

                severity_raw = record.get("info", {}).get("severity", "medium").upper()
                severity_map = {
                    "CRITICAL": Severity.CRITICAL,
                    "HIGH": Severity.HIGH,
                    "MEDIUM": Severity.MEDIUM,
                    "LOW": Severity.LOW,
                    "INFO": Severity.INFO,
                }
                severity = severity_map.get(severity_raw, Severity.MEDIUM)

                findings.append(
                    Finding(
                        title=record.get("info", {}).get("name", "Unknown nuclei finding"),
                        severity=severity,
                        description=record.get("info", {}).get("description", ""),
                        cwe=record.get("info", {}).get("classification", {}).get("cwe-id", "N/A"),
                        remediation=record.get("info", {}).get("remediation", ""),
                    )
                )

        except asyncio.TimeoutError:
            logger.error("nuclei timed out for %s", target)
        except FileNotFoundError:
            logger.error("nuclei binary not found — is it installed in the sandbox?")

        duration_ms = (datetime.now() - start).total_seconds() * 1000
        return ScanResult(
            target=target,
            scanner_name=self.name,
            findings=findings,
            duration_ms=duration_ms,
            status="completed",
        )
