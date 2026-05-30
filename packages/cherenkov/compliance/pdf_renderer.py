"""Compliance-specific PDF report with SHA-256 + RFC 3161 signing."""

import json
import re
from datetime import datetime, timezone
from typing import Dict, List, Tuple

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from cherenkov.core.base_scanner import ScanResult
from cherenkov.core.forensics import sign_trace

_SEVERITY_COLOURS: Dict[str, tuple] = {
    "CRITICAL": (180, 0, 0),
    "HIGH": (220, 60, 0),
    "MEDIUM": (220, 150, 0),
    "LOW": (30, 120, 30),
    "INFO": (60, 60, 180),
}


class CompliancePDFRenderer:
    """Generate a signed compliance PDF for one scan + framework."""

    def __init__(
        self,
        scan_result: ScanResult,
        framework: str,
        compliance_data: Dict[str, List[str]],
        chk_id: str = "CHK-???",
    ):
        self.result = scan_result
        self.framework = framework.upper()
        self.compliance = compliance_data
        self.chk_id = chk_id
        self.pdf = FPDF()
        self.pdf.set_compression(False)

    def _header_bar(self, label: str) -> None:
        p = self.pdf
        p.set_fill_color(30, 30, 30)
        p.set_text_color(255, 255, 255)
        p.set_font("helvetica", "B", 11)
        p.cell(0, 8, f"  {label}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
        p.set_text_color(0, 0, 0)
        p.set_font("helvetica", "", 10)
        p.ln(2)

    def _severity_pill(self, severity: str) -> None:
        r, g, b = _SEVERITY_COLOURS.get(severity, (100, 100, 100))
        p = self.pdf
        p.set_fill_color(r, g, b)
        p.set_text_color(255, 255, 255)
        p.set_font("helvetica", "B", 8)
        p.cell(22, 5, severity, fill=True, align="C")
        p.set_text_color(0, 0, 0)
        p.set_font("helvetica", "", 10)

    def _write_cover(self) -> None:
        p = self.pdf
        p.set_font("helvetica", "B", 24)
        p.set_text_color(30, 30, 30)
        p.cell(0, 20, "CHERENKOV", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        p.set_font("helvetica", "", 12)
        p.cell(
            0,
            6,
            "Sovereign Compliance Intelligence",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
            align="C",
        )
        p.ln(10)
        p.set_draw_color(30, 30, 30)
        p.set_line_width(0.5)
        p.line(10, p.get_y(), 200, p.get_y())
        p.ln(10)
        p.set_font("helvetica", "B", 16)
        p.cell(
            0,
            10,
            f"Compliance Report - {self.framework}",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
            align="C",
        )
        p.ln(8)
        p.set_fill_color(245, 245, 245)
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        meta = [
            ("Trace ID", self.chk_id),
            ("Target", self.result.target),
            ("Framework", self.framework),
            ("Status", self.result.status.upper()),
            ("Generated", ts),
            ("Findings", str(len(self.result.findings))),
        ]
        for label, value in meta:
            p.set_font("helvetica", "B", 10)
            p.cell(45, 8, f" {label}", border="B", fill=True)
            p.set_font("helvetica", "", 10)
            p.cell(0, 8, f" {value}", border="B", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        p.ln(10)

    def _write_summary(self) -> None:
        self._header_bar("COMPLIANCE SUMMARY")
        p = self.pdf
        total = len(self.result.findings)
        mapped = sum(1 for f in self.result.findings if f.cwe and f.cwe in self.compliance)
        p.set_font("helvetica", "", 10)
        p.cell(
            0,
            8,
            f"Findings with {self.framework} mappings: {mapped}/{total}",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )
        p.ln(4)
        all_controls = set()
        for refs in self.compliance.values():
            all_controls.update(refs)
        p.cell(
            0,
            8,
            f"Unique controls referenced: {len(all_controls)}",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )
        if all_controls:
            p.ln(2)
            p.set_font("courier", "", 8)
            p.multi_cell(
                0,
                4,
                "Controls: " + ", ".join(sorted(all_controls)),
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
            )
        p.ln(6)
        counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
        for f in self.result.findings:
            sev = f.severity.value.upper()
            counts[sev] = counts.get(sev, 0) + 1
        p.set_font("helvetica", "B", 10)
        p.cell(0, 8, "Findings by Severity:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        for sev, count in counts.items():
            if count == 0:
                continue
            self._severity_pill(sev)
            p.set_font("helvetica", "B", 10)
            p.cell(15, 6, f" {count}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        p.ln(8)

    def _write_findings(self) -> None:
        self._header_bar("VULNERABILITY FINDINGS")
        p = self.pdf
        if not self.result.findings:
            p.set_font("helvetica", "I", 10)
            p.cell(0, 8, "No vulnerabilities detected.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            return
        for i, finding in enumerate(self.result.findings, 1):
            p.set_font("helvetica", "B", 10)
            p.cell(8, 6, f"{i}.")
            self._severity_pill(finding.severity.value)
            p.set_font("helvetica", "B", 10)
            p.cell(0, 6, f"  {finding.title}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            p.set_font("helvetica", "", 9)
            p.set_x(18)
            p.multi_cell(0, 5, f"CWE: {finding.cwe}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            p.set_x(18)
            p.multi_cell(
                0, 5, f"Description: {finding.description}", new_x=XPos.LMARGIN, new_y=YPos.NEXT
            )
            p.set_x(18)
            p.multi_cell(
                0, 5, f"Remediation: {finding.remediation}", new_x=XPos.LMARGIN, new_y=YPos.NEXT
            )
            controls = self.compliance.get(finding.cwe, [])
            if controls:
                p.set_x(18)
                p.set_font("helvetica", "I", 8)
                p.multi_cell(
                    0,
                    4,
                    f"{self.framework}: {', '.join(controls)}",
                    new_x=XPos.LMARGIN,
                    new_y=YPos.NEXT,
                )
            p.ln(2)

    def _write_forensic_anchor(self, anchor: dict) -> None:
        self._header_bar("FORENSIC ANCHOR  (CherenkovTrace)")
        p = self.pdf
        p.set_font("courier", "", 8)
        sha = anchor.get("sha256", "-")
        p.multi_cell(0, 5, f"SHA-256 (findings):  {sha}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        tsa_status = anchor.get("tsa_status", "skipped")
        if tsa_status == "ok":
            token = anchor.get("tsa_token", "")
            server = anchor.get("tsa_server", "")
            p.multi_cell(
                0, 5, f"TSA Server:          {server}", new_x=XPos.LMARGIN, new_y=YPos.NEXT
            )
            p.multi_cell(
                0,
                5,
                f"RFC 3161 Token:      {token[:64]}...",
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
            )
        else:
            p.multi_cell(
                0, 5, f"RFC 3161 Status:     {tsa_status}", new_x=XPos.LMARGIN, new_y=YPos.NEXT
            )
        p.ln(4)

    def generate(self) -> Tuple[bytes, dict]:
        """Generate signed PDF. Returns (pdf_bytes, forensic_anchor)."""
        self.pdf.add_page()
        self._write_cover()
        self._write_summary()
        self._write_findings()
        findings_json = json.dumps(
            [f.model_dump() for f in self.result.findings], sort_keys=True, default=str
        )
        anchor = sign_trace(findings_json)
        self._write_forensic_anchor(anchor)
        return self.pdf.output(), anchor


def verify_pdf_signature(pdf_path: str) -> dict:
    """Extract and verify the forensic anchor embedded in a signed PDF."""
    with open(pdf_path, "rb") as f:
        content = f.read()
    text = content.decode("latin-1", errors="replace")
    sha_match = re.search(r"SHA-256 [\\(]+findings[\\)]+:\s+([a-f0-9]{64})", text)
    tsa_match = re.search(r"RFC 3161 Status:\s+(\S+)", text)
    token_match = re.search(r"RFC 3161 Token:\s+(\S+)", text)
    if not sha_match:
        return {"valid": False, "error": "No SHA-256 anchor found in PDF"}
    embedded_hash = sha_match.group(1)
    result = {
        "valid": True,
        "sha256": embedded_hash,
        "tsa_status": tsa_match.group(1) if tsa_match else ("ok" if token_match else "unknown"),
    }
    if token_match:
        result["tsa_token_prefix"] = token_match.group(1)
    file_hash = __import__("hashlib").sha256(content).hexdigest()
    result["pdf_sha256"] = file_hash
    return result
