"""Compliance Report Generation (PDF/SARIF)"""

from typing import Dict, List

from fpdf import FPDF

from cherenkov.core.base_scanner import ScanResult


class PDFReportGenerator:
    """Generates PDF reports for scan results with compliance mapping."""

    def __init__(self, scan_result: ScanResult, compliance_data: Dict[str, List[str]]):
        self.result = scan_result
        self.compliance = compliance_data
        self.pdf = FPDF()

    def generate(self) -> bytes:
        """Generate PDF content as bytes."""
        self.pdf.add_page()
        self.pdf.set_font("helvetica", "B", 16)
        self.pdf.cell(0, 10, "CHERENKOV SECURITY AUDIT REPORT", ln=True, align="C")
        self.pdf.set_font("helvetica", "", 10)
        self.pdf.cell(0, 10, f"Target: {self.result.target}", ln=True)
        self.pdf.cell(0, 10, f"Status: {self.result.status}", ln=True)
        self.pdf.cell(0, 10, f"Scanner: {self.result.scanner_name}", ln=True)
        self.pdf.ln(10)

        self.pdf.set_font("helvetica", "B", 12)
        self.pdf.cell(0, 10, "VULNERABILITY FINDINGS", ln=True)
        self.pdf.set_font("helvetica", "", 10)

        for finding in self.result.findings:
            self.pdf.set_font("helvetica", "B", 10)
            self.pdf.cell(0, 10, f"[{finding.severity}] {finding.title}", ln=True)
            self.pdf.set_font("helvetica", "", 10)
            self.pdf.multi_cell(0, 5, f"Description: {finding.description}")
            self.pdf.cell(0, 10, f"CWE: {finding.cwe}", ln=True)

            # Add compliance mapping
            mapped = self.compliance.get(finding.cwe, [])
            if mapped:
                self.pdf.set_font("helvetica", "I", 8)
                self.pdf.cell(0, 5, f"Compliance Frameworks: {', '.join(mapped)}", ln=True)
                self.pdf.set_font("helvetica", "", 10)

            self.pdf.multi_cell(0, 5, f"Remediation: {finding.remediation}")
            self.pdf.ln(5)

        return self.pdf.output()
