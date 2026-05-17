"""Compliance Report Generation (PDF/SARIF)"""

from datetime import datetime, timezone
from typing import Dict, List, Optional

from fpdf import FPDF

from cherenkov.core.base_scanner import ScanResult

_SEVERITY_COLOURS: Dict[str, tuple] = {
    "CRITICAL": (180, 0, 0),
    "HIGH":     (220, 60, 0),
    "MEDIUM":   (220, 150, 0),
    "LOW":      (30, 120, 30),
    "INFO":     (60, 60, 180),
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

    def _header_bar(self, label: str) -> None:
        self.pdf.set_fill_color(30, 30, 30)
        self.pdf.set_text_color(255, 255, 255)
        self.pdf.set_font("helvetica", "B", 11)
        self.pdf.cell(0, 8, f"  {label}", ln=True, fill=True)
        self.pdf.set_text_color(0, 0, 0)
        self.pdf.set_font("helvetica", "", 10)
        self.pdf.ln(2)

    def _severity_pill(self, severity: str) -> None:
        r, g, b = _SEVERITY_COLOURS.get(severity, (100, 100, 100))
        self.pdf.set_fill_color(r, g, b)
        self.pdf.set_text_color(255, 255, 255)
        self.pdf.set_font("helvetica", "B", 8)
        self.pdf.cell(22, 5, severity, fill=True, align="C")
        self.pdf.set_text_color(0, 0, 0)
        self.pdf.set_font("helvetica", "", 10)

    # ── sections ──────────────────────────────────────────────────────────────

    def _write_cover(self) -> None:
        self.pdf.set_font("helvetica", "B", 20)
        self.pdf.set_text_color(30, 30, 30)
        self.pdf.cell(0, 14, "CHERENKOV", ln=True, align="C")
        self.pdf.set_font("helvetica", "", 11)
        self.pdf.cell(0, 6, "Sovereign Compliance Intelligence", ln=True, align="C")
        self.pdf.ln(4)
        self.pdf.set_draw_color(30, 30, 30)
        self.pdf.set_line_width(0.5)
        self.pdf.line(10, self.pdf.get_y(), 200, self.pdf.get_y())
        self.pdf.ln(6)

        self.pdf.set_font("helvetica", "B", 13)
        self.pdf.cell(0, 8, "Security Audit Report", ln=True, align="C")
        self.pdf.ln(4)
        self.pdf.set_font("helvetica", "", 10)

        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        meta = [
            ("Trace ID",  self.chk_id),
            ("Target",    self.result.target),
            ("Status",    self.result.status),
            ("Generated", ts),
            ("Findings",  str(len(self.result.findings))),
        ]
        for label, value in meta:
            self.pdf.set_font("helvetica", "B", 10)
            self.pdf.cell(40, 7, f"{label}:", ln=False)
            self.pdf.set_font("helvetica", "", 10)
            self.pdf.cell(0, 7, value, ln=True)
        self.pdf.ln(6)

    def _write_findings(self) -> None:
        self._header_bar("VULNERABILITY FINDINGS")

        if not self.result.findings:
            self.pdf.set_font("helvetica", "I", 10)
            self.pdf.cell(0, 8, "No vulnerabilities detected.", ln=True)
            self.pdf.ln(4)
            return

        for i, finding in enumerate(self.result.findings, 1):
            self.pdf.set_font("helvetica", "B", 10)
            self.pdf.cell(8, 6, f"{i}.", ln=False)
            self._severity_pill(finding.severity.value)
            self.pdf.set_font("helvetica", "B", 10)
            self.pdf.cell(0, 6, f"  {finding.title}", ln=True)

            self.pdf.set_font("helvetica", "", 9)
            self.pdf.set_x(18)
            self.pdf.multi_cell(0, 5, f"CWE: {finding.cwe}")
            self.pdf.set_x(18)
            self.pdf.multi_cell(0, 5, f"Description: {finding.description}")
            self.pdf.set_x(18)
            self.pdf.multi_cell(0, 5, f"Remediation: {finding.remediation}")

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
                self.pdf.multi_cell(0, 4, "Compliance: " + " | ".join(frameworks))

            self.pdf.ln(4)

    def _write_forensic_anchor(self) -> None:
        if not self.anchor:
            return
        self._header_bar("FORENSIC ANCHOR  (CherenkovTrace)")
        self.pdf.set_font("courier", "", 8)

        sha = self.anchor.get("sha256", "—")
        self.pdf.multi_cell(0, 5, f"SHA-256 (findings):  {sha}")

        tsa_status = self.anchor.get("tsa_status", "skipped")
        if tsa_status == "ok":
            token = self.anchor.get("tsa_token", "")
            server = self.anchor.get("tsa_server", "")
            self.pdf.multi_cell(0, 5, f"TSA Server:          {server}")
            # Show only first 64 chars of the base64 token — the full token is in the DB
            self.pdf.multi_cell(0, 5, f"RFC 3161 Token:      {token[:64]}…")
        else:
            self.pdf.multi_cell(0, 5, f"RFC 3161 Status:     {tsa_status}")
            if tsa_status == "unavailable":
                self.pdf.set_font("helvetica", "I", 8)
                self.pdf.multi_cell(
                    0, 4,
                    "Note: TSA call skipped (air-gapped node). SHA-256 anchor is binding. "
                    "Trusted timestamp can be added post-scan via an online node.",
                )
        self.pdf.ln(4)

    # ── public ────────────────────────────────────────────────────────────────

    def generate(self) -> bytes:
        """Generate PDF content as bytes."""
        self.pdf.add_page()
        self._write_cover()
        self._write_findings()
        self._write_forensic_anchor()
        return self.pdf.output()
