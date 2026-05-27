"""Compliance Report Generation (PDF/SARIF)"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import re

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from cherenkov.core.base_scanner import ScanResult

# Arabic text support
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC_SUPPORT = True
except ImportError:
    ARABIC_SUPPORT = False

# Regex to detect Arabic characters
arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')

def contains_arabic(text):
    return bool(arabic_pattern.search(text))


_SEVERITY_COLOURS: Dict[str, tuple] = {
    "CRITICAL": (180, 0, 0),
    "HIGH": (220, 60, 0),
    "MEDIUM": (220, 150, 0),
    "LOW": (30, 120, 30),
    "INFO": (60, 60, 180),
}


class PDFReportGenerator:
    """Generates PDF reports for scan results with compliance mapping and forensic anchor."""

    def __init__(
        self,
        scan_result: ScanResult,
        compliance_data: Dict[str, List[str]],
        chk_id: str = "CHK-???",
        anchor: Optional[Dict[str, str]] = None,
    ):
        self.result = scan_result
        self.compliance = compliance_data
        self.chk_id = chk_id
        self.anchor = anchor or {}
        self.pdf = FPDF()

    # ── helpers ───────────────────────────────────────────────────────────────

    def _process_text(self, text: str) -> str:
        """Process text for Arabic shaping and bidirectional display if needed."""
        if ARABIC_SUPPORT and contains_arabic(text):
            # Reshape Arabic text
            reshaped_text = arabic_reshaper.reshape(text)
            # Apply bidirectional algorithm
            return get_display(reshaped_text)
        return text

    def _header_bar(self, label: str) -> None:
        self.pdf.set_fill_color(30, 30, 30)
        self.pdf.set_text_color(255, 255, 255)
        self.pdf.set_font("helvetica", "B", 11)
        processed_label = self._process_text(f"  {label}")
        self.pdf.cell(0, 8, processed_label, new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
        self.pdf.set_text_color(0, 0, 0)
        self.pdf.set_font("helvetica", "", 10)
        self.pdf.ln(2)

    def _severity_pill(self, severity: str) -> None:
        r, g, b = _SEVERITY_COLOURS.get(severity, (100, 100, 100))
        self.pdf.set_fill_color(r, g, b)
        self.pdf.set_text_color(255, 255, 255)
        self.pdf.set_font("helvetica", "B", 8)
        processed_severity = self._process_text(severity)
        self.pdf.cell(22, 5, processed_severity, fill=True, align="C")
        self.pdf.set_text_color(0, 0, 0)
        self.pdf.set_font("helvetica", "", 10)

    # ── sections ──────────────────────────────────────────────────────────────

    def _write_cover(self) -> None:
        self.pdf.set_font("helvetica", "B", 24)
        self.pdf.set_text_color(30, 30, 30)
        self.pdf.cell(0, 20, "CHERENKOV", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        self.pdf.set_font("helvetica", "", 12)
        self.pdf.cell(
            0,
            6,
            "Sovereign Compliance Intelligence",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
            align="C",
        )
        self.pdf.ln(10)

        self.pdf.set_draw_color(30, 30, 30)
        self.pdf.set_line_width(0.5)
        self.pdf.line(10, self.pdf.get_y(), 200, self.pdf.get_y())
        self.pdf.ln(10)

        self.pdf.set_font("helvetica", "B", 16)
        self.pdf.cell(
            0, 10, "Security Audit Report", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C"
        )
        self.pdf.ln(8)

        # Meta table-like structure
        self.pdf.set_fill_color(245, 245, 245)
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        meta = [
            ("Trace ID", self.chk_id),
            ("Target", self.result.target),
            ("Status", self.result.status.upper()),
            ("Generated", ts),
            ("Total Findings", str(len(self.result.findings))),
        ]

        for label, value in meta:
            self.pdf.set_font("helvetica", "B", 10)
            self.pdf.cell(45, 8, f" {label}", border="B", fill=True)
            self.pdf.set_font("helvetica", "", 10)
            self.pdf.cell(0, 8, f" {value}", border="B", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.pdf.ln(10)

    def _write_summary(self) -> None:
        self._header_bar("EXECUTIVE SUMMARY")

        counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
        for f in self.result.findings:
            sev = f.severity.value.upper()
            counts[sev] = counts.get(sev, 0) + 1

        self.pdf.set_font("helvetica", "B", 10)
        self.pdf.cell(0, 8, "Findings by Severity:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Draw a small bar chart or just colored boxes
        for sev, count in counts.items():
            if count == 0:
                continue
            self._severity_pill(sev)
            self.pdf.set_font("helvetica", "B", 10)
            self.pdf.cell(15, 6, f" {count}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.pdf.ln(6)

        if counts["CRITICAL"] > 0 or counts["HIGH"] > 0:
            self.pdf.set_font("helvetica", "B", 10)
            self.pdf.set_text_color(180, 0, 0)
            self.pdf.multi_cell(
                0,
                6,
                "IMMEDIATE ACTION REQUIRED: High-risk vulnerabilities were identified that may compromise the target system's integrity or confidentiality.",
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
            )
            self.pdf.set_text_color(0, 0, 0)
        else:
            self.pdf.set_font("helvetica", "I", 10)
            self.pdf.multi_cell(
                0,
                6,
                "No critical or high-severity vulnerabilities were detected during this scan.",
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
            )

        self.pdf.ln(8)

    def _write_findings(self) -> None:
        self._header_bar("VULNERABILITY FINDINGS")

        if not self.result.findings:
            self.pdf.set_font("helvetica", "I", 10)
            self.pdf.cell(0, 8, "No vulnerabilities detected.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.pdf.ln(4)
            return

        for i, finding in enumerate(self.result.findings, 1):
            self.pdf.set_font("helvetica", "B", 10)
            self.pdf.cell(8, 6, f"{i}.")
            self._severity_pill(finding.severity.value)
            self.pdf.set_font("helvetica", "B", 10)
            self.pdf.cell(0, 6, f"  {finding.title}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            self.pdf.set_font("helvetica", "", 9)
            self.pdf.set_x(18)
            self.pdf.multi_cell(0, 5, f"CWE: {finding.cwe}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.pdf.set_x(18)
            self.pdf.multi_cell(
                0, 5, f"Description: {finding.description}", new_x=XPos.LMARGIN, new_y=YPos.NEXT
            )
            self.pdf.set_x(18)
            self.pdf.multi_cell(
                0, 5, f"Remediation: {finding.remediation}", new_x=XPos.LMARGIN, new_y=YPos.NEXT
            )

            mapped = self.compliance.get(finding.cwe, {})
            if mapped:
                frameworks = []
                if isinstance(mapped, dict):
                    for fw, refs in mapped.items():
                        frameworks.append(f"{fw}: {', '.join(refs)}")
                else:
                    frameworks = list(mapped)
                self.pdf.set_x(18)
                self.pdf.set_font("helvetica", "I", 8)
                self.pdf.multi_cell(
                    0,
                    4,
                    "Compliance: " + " | ".join(frameworks),
                    new_x=XPos.LMARGIN,
                    new_y=YPos.NEXT,
                )

            self.pdf.ln(2)

    def _write_forensic_anchor(self) -> None:
        if not self.anchor:
            return
        self._header_bar("FORENSIC ANCHOR  (CherenkovTrace)")
        self.pdf.set_font("courier", "", 8)

        sha = self.anchor.get("sha256", "—")
        self.pdf.multi_cell(
            0, 5, f"SHA-256 (findings):  {sha}", new_x=XPos.LMARGIN, new_y=YPos.NEXT
        )

        tsa_status = self.anchor.get("tsa_status", "skipped")
        if tsa_status == "ok":
            token = self.anchor.get("tsa_token", "")
            server = self.anchor.get("tsa_server", "")
            self.pdf.multi_cell(
                0, 5, f"TSA Server:          {server}", new_x=XPos.LMARGIN, new_y=YPos.NEXT
            )
            # Show only first 64 chars of the base64 token — the full token is in the DB
            self.pdf.multi_cell(
                0, 5, f"RFC 3161 Token:      {token[:64]}…", new_x=XPos.LMARGIN, new_y=YPos.NEXT
            )
        else:
            self.pdf.multi_cell(
                0, 5, f"RFC 3161 Status:     {tsa_status}", new_x=XPos.LMARGIN, new_y=YPos.NEXT
            )
            if tsa_status == "unavailable":
                self.pdf.set_font("helvetica", "I", 8)
                self.pdf.multi_cell(
                    0,
                    4,
                    "Note: TSA call skipped (air-gapped node). SHA-256 anchor is binding. "
                    "Trusted timestamp can be added post-scan via an online node.",
                    new_x=XPos.LMARGIN,
                    new_y=YPos.NEXT,
                )
        self.pdf.ln(4)

    # ── public ────────────────────────────────────────────────────────────────

    def generate(self) -> bytes:
        """Generate PDF content as bytes."""
        self.pdf.add_page()
        self._write_cover()
        self._write_summary()
        self._write_findings()
        self._write_forensic_anchor()
        return self.pdf.output()


class SARIFExporter:
    """Generates SARIF 2.1.0 reports for CI/CD integration."""

    def __init__(
        self,
        scan_result: ScanResult,
        compliance_mapper: Optional[Any] = None,
        chk_id: str = "CHK-???",
    ):
        self.result = scan_result
        self.mapper = compliance_mapper
        self.chk_id = chk_id

    def generate(self) -> dict:
        """Emit SARIF 2.1.0 JSON."""
        results = []
        rules = []
        rule_ids = set()

        for f in self.result.findings:
            rule_id = f.cwe or f.title.replace(" ", "-").lower() or "unknown"

            if rule_id not in rule_ids:
                rule = {
                    "id": rule_id,
                    "shortDescription": {"text": f.title},
                    "fullDescription": {"text": f.description or f.title},
                    "properties": {
                        "precision": "very-high",
                    },
                }
                if f.cwe and "-" in f.cwe:
                    try:
                        cwe_num = f.cwe.split("-")[1]
                        rule["helpUri"] = f"https://cwe.mitre.org/data/definitions/{cwe_num}.html"
                    except (IndexError, ValueError):
                        pass
                rules.append(rule)
                rule_ids.add(rule_id)

            severity = f.severity.value.upper()
            if severity in ("CRITICAL", "HIGH"):
                level = "error"
            elif severity == "MEDIUM":
                level = "warning"
            else:
                level = "note"

            properties = {
                "remediation": f.remediation,
                "trace_id": self.chk_id,
            }

            if self.mapper and f.cwe:
                properties["compliance"] = self.mapper.map_all(f.cwe)

            results.append(
                {
                    "ruleId": rule_id,
                    "level": level,
                    "message": {"text": f.description or f.title},
                    "locations": [
                        {
                            "physicalLocation": {
                                "artifactLocation": {
                                    "uri": self.result.target,
                                },
                                "region": {"startLine": 1},
                            }
                        }
                    ],
                    "properties": properties,
                }
            )

        return {
            "$schema": "https://schemastore.org/schemas/json/sarif-2.1.0-rtm.5.json",
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "Cherenkov Scanner",
                            "version": "1.1.0",
                            "rules": rules,
                        }
                    },
                    "results": results,
                }
            ],
        }
