import asyncio
import json
import logging
from enum import Enum
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from cherenkov.core.storage.database import init_db, list_scans, save_scan

logger = logging.getLogger(__name__)

app = typer.Typer(
    name="cherenkov", help="cherenkov security scanner CLI", no_args_is_help=True
)
console = Console()

_TRACES_DIR = Path.home() / ".cherenkov" / "traces"


class OutputFormat(str, Enum):
    table = "table"
    json = "json"
    sarif = "sarif"


def _get_registry() -> "ScannerRegistry":  # noqa: F821
    try:
        from cherenkov.core.registry import ScannerRegistry

        return ScannerRegistry()
    except ImportError as exc:
        console.print(f"[red]Registry unavailable:[/red] {exc}")
        raise typer.Exit(code=1) from exc


def _next_chk_id() -> str:
    """Return the next sequential CHK-NNN trace identifier."""
    from cherenkov.core.storage.database import list_scans as _ls

    count = len(_ls(limit=100_000))
    return f"CHK-{count + 1:03d}"


def _write_pdf(chk_id: str, target: str, findings: list[dict], anchor: dict) -> Path:
    """Generate a signed PDF report and return its path."""
    from cherenkov.compliance.mapper import ComplianceMapper
    from cherenkov.compliance.reports import PDFReportGenerator
    from cherenkov.core.base_scanner import Finding, ScanResult, Severity

    mapper = ComplianceMapper()
    compliance_data = {
        f["cwe"]: mapper.map_all(f["cwe"]) for f in findings if f.get("cwe")
    }

    scan_findings = []
    for f in findings:
        try:
            scan_findings.append(
                Finding(
                    title=f["title"],
                    severity=Severity(f["severity"]),
                    description=f["description"],
                    cwe=f.get("cwe", ""),
                    remediation=f.get("remediation", ""),
                )
            )
        except Exception:
            pass

    result = ScanResult(target=target, scanner_name="cherenkov", findings=scan_findings)
    gen = PDFReportGenerator(result, compliance_data, chk_id=chk_id, anchor=anchor)

    _TRACES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = _TRACES_DIR / f"{chk_id}.pdf"
    out_path.write_bytes(gen.generate())
    return out_path


@app.command()
def scan(
    target: str = typer.Argument(..., help="Target URL or host to scan"),
    output: OutputFormat = typer.Option(
        OutputFormat.table, "--output", "-o", help="Output format"
    ),
    rps: float = typer.Option(5.0, "--rps", help="Requests per second cap"),
    pdf: bool = typer.Option(
        False, "--pdf", "-p", help="Generate signed PDF report to ~/.cherenkov/traces/"
    ),
) -> None:
    """Run all registered scanners against TARGET."""
    import uuid
    from datetime import datetime, timezone

    from cherenkov.core.engine import ScanEngine
    from cherenkov.core.forensics import sign_trace
    from cherenkov.core.registry import ScannerRegistry

    init_db()
    chk_id = _next_chk_id()
    scan_id = str(uuid.uuid4())
    started = datetime.now(timezone.utc).isoformat()
    console.print(f"[bold]Illuminating target[/bold] {target}  ({chk_id}, rps={rps})")

    try:
        registry = ScannerRegistry()
        engine = ScanEngine(registry)
        scan_results = asyncio.run(engine.scan_all(target, timeout=10.0))
    except Exception as exc:
        logger.error("ScanEngine execution failed for %s: %s", target, exc)
        console.print(f"[red]Scan failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    findings: list[dict] = []
    for scanner_name, result in scan_results.items():
        for f in result.findings:
            findings.append(
                {
                    "scanner": scanner_name,
                    "title": f.title,
                    "severity": f.severity.value,
                    "cwe": f.cwe,
                    "description": f.description,
                    "remediation": f.remediation,
                }
            )

    # Sign findings — SHA-256 + best-effort RFC 3161 timestamp
    anchor = sign_trace(json.dumps(findings, sort_keys=True))
    tsa_note = (
        "RFC 3161 ✓"
        if anchor.get("tsa_status") == "ok"
        else f"TSA {anchor.get('tsa_status')}"
    )
    console.print(f"[dim]sha256: {anchor['sha256'][:16]}…  {tsa_note}[/dim]")

    finished = datetime.now(timezone.utc).isoformat()
    save_scan(
        scan_id,
        target,
        findings,
        meta={
            "chk_id": chk_id,
            "rps": rps,
            "scanners_run": list(scan_results.keys()),
            "anchor": anchor,
        },
        started_at=started,
        finished_at=finished,
    )

    if output == OutputFormat.json:
        console.print_json(
            json.dumps(
                {
                    "scan_id": scan_id,
                    "chk_id": chk_id,
                    "target": target,
                    "findings": findings,
                    "anchor": anchor,
                }
            )
        )
    elif output == OutputFormat.sarif:
        sarif_results = [
            {
                "ruleId": f.get("cwe", ""),
                "message": {"text": f.get("title", "")},
                "level": f.get("severity", "none").lower(),
            }
            for f in findings
        ]
        sarif = {
            "version": "2.1.0",
            "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
            "runs": [
                {
                    "tool": {"driver": {"name": "cherenkov", "rules": []}},
                    "results": sarif_results,
                }
            ],
        }
        console.print_json(json.dumps(sarif))
    else:
        t = Table(
            "Finding",
            "Severity",
            "CWE",
            "Scanner",
            title=f"Cherenkov Trace {chk_id} — {target}",
        )
        for f in findings:
            t.add_row(
                f.get("title", ""),
                f.get("severity", ""),
                f.get("cwe", ""),
                f.get("scanner", ""),
            )
        console.print(t if findings else "[green]No anomalies isolated.[/green]")

    if pdf:
        pdf_path = _write_pdf(chk_id, target, findings, anchor)
        console.print(f"[green]PDF report:[/green] {pdf_path}")

    console.print(f"[dim]scan_id: {scan_id}[/dim]")


@app.command()
def history(
    n: int = typer.Option(20, "-n", help="Number of recent scans to show"),
) -> None:
    """Show the N most recent scan results."""
    init_db()
    rows = list_scans(limit=n)
    if not rows:
        console.print("[yellow]No scan history found.[/yellow]")
        return
    t = Table("chk_id", "scan_id", "target", "status", "started_at", "findings #")
    for r in rows:
        chk_id = r.get("meta", {}).get("chk_id", "—")
        t.add_row(
            chk_id,
            r["scan_id"][:8] + "…",
            r["target"],
            r["status"],
            r["started_at"],
            str(len(r["findings"])),
        )
    console.print(t)


@app.command(name="list-scanners")
def list_scanners() -> None:
    """List all registered scanners."""
    registry = _get_registry()
    names = registry.list_scanners()
    if not names:
        console.print("[yellow]No scanners registered.[/yellow]")
        return
    t = Table("Name", "CWE", "Description")
    for name in names:
        scanner_cls = registry.get_scanner(name)
        t.add_row(
            name,
            getattr(scanner_cls, "cwe", "—"),
            getattr(scanner_cls, "__doc__", "—") or "—",
        )
    console.print(t)


reasoning_app = typer.Typer(name="reasoning", help="Manage and inspect reasoning logs")
app.add_typer(reasoning_app)


@reasoning_app.command("show")
def reasoning_show(
    session_id: str = typer.Argument(..., help="Session ID of the reasoning trace")
):
    """Display a human-readable reasoning log for the specified session."""
    from cherenkov.core.reasoning_store import ReasoningStore

    store = ReasoningStore(session_id)
    traces = store.query()

    if not traces:
        console.print(
            f"[yellow]No reasoning traces found for session: {session_id}[/yellow]"
        )
        return

    for trace in traces:
        step = trace.get("step_index", 0)
        tool = trace.get("tool_name", "unknown")
        model = trace.get("model", "unknown")
        duration = trace.get("duration_ms", 0)
        agent = trace.get("agent", "unknown")
        reasoning = trace.get("reasoning", "")
        confidence = trace.get("confidence", 0.0)
        sha256 = trace.get("sha256", "")
        short_sha = sha256[:8] if sha256 else ""

        console.print(f"[Step {step:02d} | {tool} | {model} | {duration}ms]")
        console.print(f"Agent : {agent}")
        console.print(f'Reasoning: "{reasoning}"')
        console.print(f"Confidence: {confidence}")
        console.print(f"SHA256: {short_sha}...")
        console.print()


@reasoning_app.command("export")
def reasoning_export(
    session_id: str = typer.Argument(..., help="Session ID of the reasoning trace"),
    out: str = typer.Argument(..., help="Output JSONL file path"),
):
    """Export reasoning log to a JSONL file."""
    from cherenkov.core.reasoning_store import ReasoningStore

    store = ReasoningStore(session_id)
    store.export_jsonl(out)
    console.print(f"[green]Exported traces for session {session_id} to {out}[/green]")


@reasoning_app.command("verify")
def reasoning_verify(
    session_id: str = typer.Argument(..., help="Session ID of the reasoning trace")
):
    """Re-compute SHA-256 anchors for all rows to detect tampering."""
    from cherenkov.core.reasoning_store import ReasoningStore

    store = ReasoningStore(session_id)
    results = store.verify_hashes()

    if not results:
        console.print(
            f"[yellow]No reasoning traces found for session: {session_id}[/yellow]"
        )
        return

    failures = 0
    for res in results:
        step = res["step_index"]
        status = res["status"]
        if status == "PASS":
            short_sha = res["stored"] if res["stored"] else ""
            console.print(
                f"[{status}] Step {step:02d} | trace_id={session_id} | anchor={short_sha}..."
            )
        else:
            failures += 1
            stored = res["stored"] if res["stored"] else "..."
            recomputed = res["recomputed"] if res["recomputed"] else "..."
            console.print(
                f"[{status}] Step {step:02d} | trace_id={session_id} | stored={stored} recomputed={recomputed}"
            )

    if failures > 0:
        console.print(
            f"\n[red]Tamper detected: {failures} of {len(results)} steps failed anchor verification.[/red]"
        )
    else:
        console.print(
            f"\n[green]All {len(results)} steps passed anchor verification.[/green]"
        )


if __name__ == "__main__":
    app()
