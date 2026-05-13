import asyncio
import json
import logging
from enum import Enum

import typer
from rich.console import Console
from rich.table import Table

from cherenkov.core.storage.database import init_db, list_scans, save_scan

logger = logging.getLogger(__name__)

app = typer.Typer(name="cherenkov", help="cherenkov security scanner CLI", no_args_is_help=True)
console = Console()


class OutputFormat(str, Enum):
    table = "table"
    json = "json"
    sarif = "sarif"


def _get_registry() -> "ScannerRegistry":  # noqa: F821
    # Lazy import — registry pulls pydantic which may not be installed in minimal envs.
    try:
        from cherenkov.core.registry import ScannerRegistry

        return ScannerRegistry()
    except ImportError as exc:
        console.print(f"[red]Registry unavailable:[/red] {exc}")
        raise typer.Exit(code=1) from exc


@app.command()
def scan(
    target: str = typer.Argument(..., help="Target URL or host to scan"),
    output: OutputFormat = typer.Option(OutputFormat.table, "--output", "-o", help="Output format"),
    rps: float = typer.Option(5.0, "--rps", help="Requests per second cap"),
) -> None:
    """Run all registered scanners against TARGET."""
    import uuid
    from datetime import datetime, timezone

    from cherenkov.core.engine import ScanEngine
    from cherenkov.core.registry import ScannerRegistry

    init_db()
    scan_id = str(uuid.uuid4())
    started = datetime.now(timezone.utc).isoformat()
    console.print(f"[bold]Illuminating target[/bold] {target}  (rps={rps}, output={output.value})")

    # Wire execution through ScanEngine — replaces empty placeholder list
    try:
        registry = ScannerRegistry()
        engine = ScanEngine(registry)
        scan_results = asyncio.run(engine.scan_all(target, timeout=10.0))
    except Exception as exc:
        logger.error("ScanEngine execution failed for %s: %s", target, exc)
        console.print(f"[red]Scan failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    # Flatten ScanResult objects → plain dicts for storage and display
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

    finished = datetime.now(timezone.utc).isoformat()
    save_scan(
        scan_id,
        target,
        findings,
        meta={"rps": rps, "scanners_run": list(scan_results.keys())},
        started_at=started,
        finished_at=finished,
    )

    if output == OutputFormat.json:
        console.print_json(json.dumps({"scan_id": scan_id, "target": target, "findings": findings}))
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
        t = Table("Finding", "Severity", "CWE", "Scanner", title=f"Cherenkov Trace — {target}")
        for f in findings:
            t.add_row(
                f.get("title", ""), f.get("severity", ""), f.get("cwe", ""), f.get("scanner", "")
            )
        console.print(t if findings else "[green]No anomalies isolated.[/green]")

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
    t = Table("scan_id", "target", "status", "started_at", "findings #")
    for r in rows:
        t.add_row(r["scan_id"], r["target"], r["status"], r["started_at"], str(len(r["findings"])))
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
            name, getattr(scanner_cls, "cwe", "—"), getattr(scanner_cls, "__doc__", "—") or "—"
        )
    console.print(t)


if __name__ == "__main__":
    app()
