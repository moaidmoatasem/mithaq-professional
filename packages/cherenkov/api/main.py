"""
cherenkov REST API Server
FastAPI-based API for security scanning, workflow orchestration, and the web dashboard.

Flask has been retired. The dashboard is now served as static HTML from
packages/cherenkov/api/static/index.html via FastAPI StaticFiles.
"""

import asyncio
import json
import logging
import os
import re
import sqlite3
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Literal, Optional, Set
from urllib.parse import urlparse

import httpx
from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.routing import APIRouter
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from cherenkov.api.middleware.auth import (
    Role,
    RoleChecker,
    create_access_token,
    get_current_user,
    verify_password,
)
from cherenkov.api.middleware.auth import (
    User as AuthUser,
)
from cherenkov.core.base_scanner import ScanResult
from cherenkov.core.storage.database import (
    _DB_PATH,
    get_audit_log,
    get_user,
    save_audit_entry,
)
from cherenkov.core.tokamak import Command, Tokamak
from cherenkov.orchestration.orchestration_api import orchestrate_workflow
from cherenkov.orchestration.result_persistence import ResultStore
from cherenkov.orchestration.workflow_parser import load_workflow
from cherenkov.core.siem import SIEMForwarder
from cherenkov.core.mesh import MeshManager
from cherenkov.core.storage.lattice import LatticeBridge
from cherenkov.threat_modeling import DFDGenerator, ThreatDragonExporter, TMBOMExporter, MermaidExporter
from cherenkov.threat_modeling.schemas import ThreatModel, Diagram, DFDItem, DFDItemType, Threat, Severity, Control, ControlStatus, Risk

logger = logging.getLogger(__name__)

# Enterprise Integrations
siem = SIEMForwarder({"enabled": True, "mode": "syslog", "host": "127.0.0.1", "port": 514})
mesh = MeshManager()
lattice = LatticeBridge()

_STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    from cherenkov.core.circuit_breaker import meissner_hub

    meissner_hub.on_open(
        lambda: asyncio.create_task(
            _broadcast({"type": "circuit_breaker", "state": "OPEN", "reason": "threshold_exceeded"})
        )
    )
    meissner_hub.on_close(
        lambda: asyncio.create_task(
            _broadcast({"type": "circuit_breaker", "state": "CLOSED", "reason": "recovery_successful"})
        )
    )
    meissner_hub.on_half_open(
        lambda: asyncio.create_task(
            _broadcast({"type": "circuit_breaker", "state": "HALF_OPEN", "reason": "testing_recovery"})
        )
    )
    # Initialize LATTICE collection
    asyncio.create_task(lattice.init_collection())
    yield


app = FastAPI(
    title="cherenkov Sovereign Security API",
    description="Scan API, workflow orchestration, and web dashboard. Flask retired.",
    version="1.1.0",
    lifespan=lifespan,
)


# Include localhost:3000 (React dev server) alongside the API host origins
_ALLOWED_ORIGINS = os.getenv(
    "cherenkov_CORS_ORIGINS",
    "http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000,http://127.0.0.1:3000",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── WebSocket live-event broadcast ───────────────────────────────────────────

_ws_clients: Set[WebSocket] = set()


async def _broadcast(event: dict) -> None:
    """Push a JSON event to every connected WebSocket client."""
    dead: Set[WebSocket] = set()
    payload = json.dumps(event)
    for ws in list(_ws_clients):
        try:
            await ws.send_text(payload)
        except Exception:
            dead.add(ws)
    _ws_clients.difference_update(dead)


@app.websocket("/ws/live")
async def ws_live(websocket: WebSocket) -> None:
    """Live event stream for the CHERENKOV web dashboard."""
    await websocket.accept()
    _ws_clients.add(websocket)
    try:
        while True:
            # Keep-alive: echo any client ping, otherwise just wait
            await asyncio.sleep(30)
            await websocket.send_text(json.dumps({"type": "ping"}))
    except WebSocketDisconnect:
        pass
    finally:
        _ws_clients.discard(websocket)


# ── /api/v1 router (consumed by the React frontend) ─────────────────────────


class SandboxExecuteRequest(BaseModel):
    payload: str
    timeout: int = 30


v1 = APIRouter(prefix="/api/v1")


class AuthRequest(BaseModel):
    username: str
    password: str


@v1.post("/auth/token")
async def v1_auth_token(request: AuthRequest) -> dict:
    """Authenticate a user and return a JWT token."""
    user_data = get_user(request.username)
    if not user_data or not verify_password(request.password, user_data["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = create_access_token(data={"sub": request.username, "role": user_data["role"]})
    return {"access_token": access_token, "token_type": "bearer"}


@v1.get("/auth/me")
async def v1_auth_me(current_user: AuthUser = Depends(get_current_user)) -> dict:
    """Return the current authenticated user's profile."""
    return {"username": current_user.username, "role": current_user.role.name}


@v1.get("/audit")
async def v1_audit_log(current_user: AuthUser = Depends(RoleChecker(Role.ADMIN))) -> list[dict]:
    """Return the CHERENKOV audit log. Requires ADMIN role."""
    return get_audit_log(100)


async def _check_ollama() -> str:
    try:
        async with httpx.AsyncClient(timeout=1.0) as c:
            r = await c.get("http://localhost:11434/api/tags")
            return "ready" if r.status_code == 200 else "offline"
    except Exception:
        return "offline"


def _get_active_scans_count() -> int:
    try:
        with sqlite3.connect(_DB_PATH) as conn:
            return conn.execute("SELECT count(*) FROM scans WHERE status = 'running'").fetchone()[0]
    except Exception:
        return 0


@v1.get("/health")
async def v1_health() -> dict:
    """Health check used by useMetrics / useQueueDepth hooks.

    Returns the node topology expected by NodeStatusRow and
    the Meissner shield state expected by ForensicHeader.
    """
    from cherenkov.core.circuit_breaker import meissner_hub

    active_scans = _get_active_scans_count()

    ollama_status = await _check_ollama()
    meissner_state = meissner_hub.state.value.upper()

    return {
        "status": "healthy",
        "agents": "operational",
        "queue": {"scan_jobs_pending": active_scans},
        "uptime": time.time(),
        "active_scans": active_scans,
        "meissner": {"state": meissner_state},
        "nodes": {
            "tensor": {"status": ollama_status, "model": "Llama 3.1 8B"},
            "kinetic": {"status": ollama_status, "model": "Qwen2.5 3B", "ram_gb": 8},
            "aegis": {"status": ollama_status, "model": "Llama 3.1 8B", "ram_gb": 8},
            "lattice": {"status": "ready", "model": "Qdrant / Vector", "vector_count": 0},
            "tokamak": {"status": "ready", "model": "Sandbox Ready", "active_containers": 0},
        },
    }


@v1.get("/ablation/stats")
async def v1_ablation_stats() -> dict:
    """Return ABLATION sanitization telemetry for the AblationMeter widget."""
    try:
        from cherenkov.core.ablation.bridge import AblationBridge

        bridge = AblationBridge.instance() if hasattr(AblationBridge, "instance") else None
        if bridge and hasattr(bridge, "telemetry"):
            t = bridge.telemetry
            drop_rate = t.drops / t.attempts if t.attempts else 0.0
            return {
                "session_stats": {
                    "attempts": t.attempts,
                    "drops": t.drops,
                    "drop_rate": drop_rate,
                    "alert_active": drop_rate > 0.2,
                }
            }
    except Exception:
        pass
    # Fallback: healthy zeros when the bridge is not yet active
    return {
        "session_stats": {
            "attempts": 0,
            "drops": 0,
            "drop_rate": 0.0,
            "alert_active": False,
        }
    }


@v1.post("/sandbox/execute")
async def v1_sandbox_execute(
    command: Command, current_user: AuthUser = Depends(RoleChecker(Role.OPERATOR))
) -> dict:
    """Execute a payload in the TOKAMAK sandbox. Requires OPERATOR role."""
    result = await asyncio.to_thread(Tokamak.execute, command)
    return {
        "status": "success",
        "stdout": result.stdout,
        "stderr": result.stderr,
        "trace_hash": result.trace_hash,
        "shred_receipt": result.shred_receipt,
        "exit_code": result.exit_code,
        "duration_ms": result.duration_ms,
    }


@v1.get("/sandbox/status")
async def v1_sandbox_status(current_user: AuthUser = Depends(get_current_user)) -> dict:
    """Return the status of the TOKAMAK sandbox."""
    return {"status": "operational", "containers_active": 0}


@v1.get("/mesh/nodes")
async def v1_mesh_nodes(current_user: AuthUser = Depends(RoleChecker(Role.ADMIN))) -> list[dict]:
    """Return list of active mesh nodes. Requires ADMIN."""
    return mesh.get_active_nodes()


@v1.post("/mesh/register")
async def v1_mesh_register(node_id: str, host: str, role: str = "worker") -> dict:
    """Register a new node in the mesh."""
    mesh.register_node(node_id, host, role)
    return {"status": "registered", "node_id": node_id}


@v1.post("/mobile/scan")
async def v1_mobile_scan(
    request: ScanRequest, current_user: AuthUser = Depends(get_current_user)
) -> dict:
    """Specialized mobile binary analysis; triggers IPA/APK forensic scanners."""
    # For now, we reuse _run_scan but could add mobile-specific logic here
    return await _run_scan(request)


@v1.post("/scan")
async def v1_scan(
    request: "ScanRequest", current_user: AuthUser = Depends(get_current_user)
) -> dict:
    """Proxy to the core scan engine; broadcasts a live event on completion."""
    result = await _run_scan(request)

    # Audit log
    save_audit_entry(
        event_type="SCAN_INITIATED",
        user_id=current_user.username,
        details={"target": request.url, "scan_id": result["scan_id"]},
    )

    await _broadcast(
        {
            "type": "scan_complete",
            "scan_id": result["scan_id"],
            "target": result["target"],
            "count": result["count"],
            "timestamp": result["timestamp"],
        }
    )
    return result


@v1.get("/scans/history")
async def v1_scan_history() -> list[dict]:
    """Return recent scan results for the ThreatIntelPanel sidebar."""
    from cherenkov.core.storage.database import list_scans

    return list_scans(20)


@v1.get("/reports/{scan_id}/sarif")
async def v1_scan_report_sarif(scan_id: str) -> dict:
    """Return a scan report in SARIF 2.1.0 format."""
    from cherenkov.compliance.mapper import ComplianceMapper
    from cherenkov.core.storage.database import get_scan

    scan = get_scan(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    results = []
    for f in scan.get("findings", []):
        severity = str(f.get("severity", "")).upper()
        if severity in ("CRITICAL", "HIGH"):
            level = "error"
        elif severity == "MEDIUM":
            level = "warning"
        else:
            level = "note"

        cwe = f.get("cwe")
        properties = {
            "scanner": f.get("scanner", "unknown"),
            "remediation": f.get("remediation", ""),
        }
        if cwe:
            properties["compliance"] = {
                "OWASP": ComplianceMapper.map(cwe, "OWASP"),
                "SAMA_CSF": ComplianceMapper.map(cwe, "SAMA_CSF"),
                "EGY_FIN_CSF": ComplianceMapper.map(cwe, "EGY_FIN_CSF"),
                "DORA": ComplianceMapper.map(cwe, "DORA"),
            }

        results.append(
            {
                "ruleId": cwe or f.get("type") or "unknown",
                "level": level,
                "message": {"text": f.get("description", "No description provided.")},
                "properties": properties,
            }
        )

    return {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "Cherenkov Scanner",
                        "version": "1.1.0",
                    }
                },
                "results": results,
            }
        ],
    }


@v1.get("/reports/{scan_id}/pdf")
async def v1_scan_report_pdf(scan_id: str) -> FileResponse:
    from io import BytesIO

    from fastapi.responses import Response
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    from cherenkov.compliance.mapper import ComplianceMapper
    from cherenkov.core.storage.database import get_scan

    scan = get_scan(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"CHERENKOV Audit Report — {scan_id}", styles["Title"]))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(f"<b>Target:</b> {scan.get('target', 'N/A')}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Status:</b> {scan.get('status', 'N/A')}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Started:</b> {scan.get('started_at', 'N/A')}", styles["Normal"]))
    elements.append(
        Paragraph(f"<b>Finished:</b> {scan.get('finished_at', 'N/A')}", styles["Normal"])
    )
    elements.append(
        Paragraph(
            "<b>Compliance Frameworks:</b> OWASP Top 10, SAMA CSF, EGY-FIN CSF, DORA",
            styles["Normal"],
        )
    )
    elements.append(Spacer(1, 0.3 * inch))

    findings = scan.get("findings", [])
    if findings:
        elements.append(Paragraph(f"Findings ({len(findings)})", styles["Heading2"]))
        elements.append(Spacer(1, 0.1 * inch))
        table_data = [["Severity", "CWE", "Description", "OWASP", "SAMA", "EGY-FIN", "DORA"]]
        for f in findings:
            cwe = f.get("cwe", "")
            sev = str(f.get("severity", "")).upper()
            desc = f.get("description", "")[:60]
            owasp = ", ".join(ComplianceMapper.map(cwe, "OWASP")) if cwe else ""
            sama = ", ".join(ComplianceMapper.map(cwe, "SAMA_CSF")) if cwe else ""
            egy = ", ".join(ComplianceMapper.map(cwe, "EGY_FIN_CSF")) if cwe else ""
            dora = ", ".join(ComplianceMapper.map(cwe, "DORA")) if cwe else ""
            table_data.append([sev, cwe, desc, owasp, sama, egy, dora])

        col_widths = [
            0.5 * inch,
            0.6 * inch,
            1.6 * inch,
            0.9 * inch,
            0.9 * inch,
            0.9 * inch,
            0.9 * inch,
        ]
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 8),
                    ("FONTSIZE", (0, 1), (-1, -1), 7),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        elements.append(table)
    else:
        elements.append(Paragraph("No findings in this scan.", styles["Normal"]))

    elements.append(Spacer(1, 0.3 * inch))
    elements.append(
        Paragraph(
            "<i>Generated by CHERENKOV Security Platform — this report is a forensic artifact.</i>",
            styles["Italic"],
        )
    )

    doc.build(elements)
    pdf_bytes = buf.getvalue()
    buf.close()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="cherenkov-report-{scan_id}.pdf"'},
    )


@v1.get("/processes")
async def v1_list_processes(category: Optional[str] = None) -> dict:
    """List available business processes for security mapping."""
    from cherenkov.compliance.process_mapper import ProcessMapper

    processes = ProcessMapper.list_processes(category)
    categories = ProcessMapper.list_categories()
    return {"processes": processes, "categories": categories, "count": len(processes)}


@v1.get("/processes/{process_id}")
async def v1_get_process(process_id: str) -> dict:
    """Get a business process with steps and mapped security controls."""
    from cherenkov.compliance.process_mapper import ProcessMapper

    process = ProcessMapper.get_process(process_id)
    if not process:
        raise HTTPException(status_code=404, detail="Process not found")
    return process


@v1.get("/processes/{process_id}/controls")
async def v1_get_process_controls(process_id: str, framework: Optional[str] = None) -> dict:
    """Get security controls for a process, optionally filtered by compliance framework."""
    from cherenkov.compliance.process_mapper import ProcessMapper

    result = ProcessMapper.get_process_controls(process_id, framework)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@v1.get("/processes/{process_id}/report")
async def v1_get_process_report(process_id: str) -> dict:
    """Generate a comprehensive risk report for a business process."""
    from cherenkov.compliance.process_mapper import ProcessMapper

    report = ProcessMapper.generate_risk_report(process_id)
    if "error" in report:
        raise HTTPException(status_code=404, detail=report["error"])
    return report


@v1.get("/findings/pending")
async def v1_get_pending_findings() -> list[dict]:
    """Return a list of all pending findings."""
    from cherenkov.core.storage.database import get_pending_findings, init_db

    try:
        init_db()
        return get_pending_findings()
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Failed to get pending findings: {exc}"
        ) from exc


@v1.post("/findings/{finding_id}/approve")
async def v1_approve_finding(
    finding_id: str, current_user: AuthUser = Depends(RoleChecker(Role.OPERATOR))
) -> dict:
    """Approve a finding. Requires OPERATOR role or higher."""
    from cherenkov.core.storage.database import init_db, update_finding_status

    try:
        init_db()
        update_finding_status(finding_id, "approved", current_user.username)

        # Audit log
        save_audit_entry(
            event_type="FINDING_APPROVED",
            user_id=current_user.username,
            details={"finding_id": finding_id},
        )

        return {"status": "success", "finding_id": finding_id, "new_status": "approved"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to approve finding: {exc}") from exc


@v1.post("/findings/{finding_id}/reject")
async def v1_reject_finding(
    finding_id: str, current_user: AuthUser = Depends(RoleChecker(Role.OPERATOR))
) -> dict:
    """Reject a finding. Requires OPERATOR role or higher."""
    from cherenkov.core.storage.database import init_db, update_finding_status

    try:
        init_db()
        update_finding_status(finding_id, "rejected", current_user.username)

        # Audit log
        save_audit_entry(
            event_type="FINDING_REJECTED",
            user_id=current_user.username,
            details={"finding_id": finding_id},
        )

        return {"status": "success", "finding_id": finding_id, "new_status": "rejected"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to reject finding: {exc}") from exc


# Serve the static dashboard assets
if _STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")


# ── Models ──────────────────────────────────────────────────────────────────


class ScanRequest(BaseModel):
    url: str


class FindingApproval(BaseModel):
    finding_id: str
    severity: str
    scanner: str
    title: str
    status: Literal["pending", "approved", "rejected"]
    operator_id: Optional[str] = None
    approved_at: Optional[str] = None


class WorkflowExecuteRequest(BaseModel):
    workflow_name: str
    config: Optional[Dict[str, Any]] = None


class WorkflowResponse(BaseModel):
    success: bool
    workflow: str
    outputs: Dict[str, Any]
    duration: float


# ── Dashboard ────────────────────────────────────────────────────────────────


@app.get("/", include_in_schema=False)
async def dashboard() -> FileResponse:
    """Serve the CHERENKOV web dashboard (replaces retired Flask app)."""
    index = _STATIC_DIR / "index.html"
    if not index.exists():
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return FileResponse(str(index), media_type="text/html")


# ── Shared scan implementation ────────────────────────────────────────────────


async def _forward_to_siem(vulnerabilities: list[dict], target: str):
    """Background task to forward findings to local SIEM."""
    from cherenkov.core.siem import SIEMForwarder

    for v in vulnerabilities:
        finding = {**v, "target": target}
        # Default local syslog forward (UDP 514)
        SIEMForwarder.send_syslog(finding)
        logger.debug("Forwarded finding to local SIEM: %s", v["title"])


async def _run_scan(request: "ScanRequest") -> dict:
    """Core scan logic shared by /api/scan and /api/v1/scan."""
    from cherenkov.core.engine import ScanEngine
    from cherenkov.core.registry import ScannerRegistry
    from cherenkov.core.storage.database import init_db, save_scan

    try:
        parsed = urlparse(request.url)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid URL: {exc}") from exc

    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="Only http/https URLs are supported")
    if not parsed.netloc:
        raise HTTPException(status_code=400, detail="Invalid URL: missing hostname")

    scan_id = str(uuid.uuid4())
    started = datetime.now(timezone.utc).isoformat()

    async def on_progress(scanner_name: str, result: ScanResult):
        await _broadcast(
            {
                "type": "scan_progress",
                "scan_id": scan_id,
                "scanner": scanner_name,
                "status": result.status,
                "findings_count": len(result.findings),
            }
        )

    try:
        registry = ScannerRegistry()
        total_scanners = len(registry.list_scanners())

        await _broadcast(
            {
                "type": "scan_started",
                "scan_id": scan_id,
                "target": request.url,
                "total_scanners": total_scanners,
                "timestamp": started,
            }
        )

        engine = ScanEngine(registry)
        scan_results = await engine.scan_all(request.url, timeout=10.0, on_progress=on_progress)
    except Exception as exc:
        logger.error("ScanEngine failed for %s: %s", request.url, exc)
        raise HTTPException(status_code=500, detail=f"Scan execution failed: {exc}") from exc

    vulnerabilities: list[dict] = []
    for scanner_name, result in scan_results.items():
        for f in result.findings:
            vulnerabilities.append(
                {
                    "scanner": scanner_name,
                    "title": f.title,
                    "type": f.title,
                    "severity": f.severity.value,
                    "cwe": f.cwe,
                    "description": f.description,
                    "remediation": f.remediation,
                }
            )

    finished = datetime.now(timezone.utc).isoformat()

    try:
        init_db()
        save_scan(
            scan_id,
            request.url,
            vulnerabilities,
            meta={"scanners_run": list(scan_results.keys())},
            started_at=started,
            finished_at=finished,
        )

        from cherenkov.core.storage.database import save_pending_finding

        for v in vulnerabilities:
            if v["severity"] in ("CRITICAL", "HIGH"):
                finding_id = str(uuid.uuid4())
                save_pending_finding(
                    finding_id=finding_id,
                    severity=v["severity"],
                    scanner=v["scanner"],
                    title=v["title"],
                    scan_id=scan_id,
                )

                # We need to await the broadcast event, but broadcast relies on asyncio loop running.
                # Since _run_scan is async, we can await it directly.
                asyncio.create_task(
                    _broadcast(
                        {
                            "type": "finding_discovered",
                            "finding_id": finding_id,
                            "severity": v["severity"],
                        }
                    )
                )

                # SIEM Forwarding
                asyncio.create_task(siem.forward_finding(v, {"target": request.url, "scan_id": scan_id, "timestamp": finished}))

                # LATTICE Embedding
                asyncio.create_task(lattice.embed_and_store(
                    finding_id=finding_id,
                    content=f"{v['title']}: {v['description']}",
                    metadata={"target": request.url, "scanner": v["scanner"], "severity": v["severity"]}
                ))

    except Exception as exc:
        logger.error("Failed to persist scan %s: %s", scan_id, exc)

    # Trigger SIEM forwarding
    asyncio.create_task(_forward_to_siem(vulnerabilities, request.url))

    return {
        "scan_id": scan_id,
        "target": request.url,
        "timestamp": finished,
        "vulnerabilities": vulnerabilities,
        "count": len(vulnerabilities),
    }


# ── Threat Modeling API ──────────────────────────────────────────────────────


class ThreatModelGenerateRequest(BaseModel):
    description: str
    owner: str = "Security Team"
    architecture_pattern: str = "web_app"


@v1.post("/threat-model/generate")
async def v1_threat_model_generate(
    request: ThreatModelGenerateRequest,
    current_user: AuthUser = Depends(get_current_user),
) -> dict:
    """Generate a complete threat model (DFD + STRIDE) from a system description.

    Uses template-based generation with optional LLM enrichment via Ollama.
    Returns the model summary and available export formats.
    """
    import json

    from cherenkov.agents.local.ollama_client import OllamaClient

    llm = OllamaClient() if OllamaClient().is_available() else None
    generator = DFDGenerator(llm_client=llm)

    model = generator.generate(
        system_description=request.description,
        architecture_pattern=request.architecture_pattern,
        owner=request.owner,
    )

    model_id = str(uuid.uuid4())

    td_exporter = ThreatDragonExporter(model)
    td_json = td_exporter.export()

    tmbom_exporter = TMBOMExporter(model)
    tmbom_json = tmbom_exporter.export()

    mermaid_exporter = MermaidExporter(model)
    mermaid_dfd = mermaid_exporter.export_flowchart()

    from cherenkov.core.storage.database import save_threat_model

    save_threat_model(
        model_id=model_id,
        title=model.title,
        owner=model.owner,
        description=model.description,
        version=model.version,
        model_json=json.dumps({
            "diagrams": [
                {
                    "title": d.title,
                    "type": d.diagram_type,
                    "item_count": len(d.items),
                    "threat_count": len(d.threats),
                }
                for d in model.diagrams
            ],
            "control_count": len(model.controls),
            "risk_count": len(model.risks),
        }),
        threat_dragon_json=json.dumps(td_json),
        tmbom_json=json.dumps(tmbom_json),
        mermaid_dfd=mermaid_dfd,
    )

    asyncio.create_task(
        _broadcast({
            "type": "threat_model_generated",
            "model_id": model_id,
            "title": model.title,
            "threat_count": sum(len(d.threats) for d in model.diagrams),
        })
    )

    return {
        "model_id": model_id,
        "title": model.title,
        "description": model.description[:200],
        "owner": model.owner,
        "version": model.version,
        "diagrams": [
            {
                "title": d.title,
                "type": d.diagram_type,
                "items": len(d.items),
                "threats": len(d.threats),
            }
            for d in model.diagrams
        ],
        "controls": len(model.controls),
        "risks": len(model.risks),
        "exports": {
            "threat_dragon": f"/api/v1/threat-model/{model_id}/export/threat-dragon",
            "tmbom": f"/api/v1/threat-model/{model_id}/export/tmbom",
            "mermaid": f"/api/v1/threat-model/{model_id}/export/dfd",
        },
    }


@v1.get("/threat-model/{model_id}")
async def v1_get_threat_model(
    model_id: str,
    current_user: AuthUser = Depends(get_current_user),
) -> dict:
    """Retrieve a stored threat model by ID."""
    from cherenkov.core.storage.database import get_threat_model

    tm = get_threat_model(model_id)
    if not tm:
        raise HTTPException(status_code=404, detail="Threat model not found")
    return {
        "model_id": tm["model_id"],
        "title": tm["title"],
        "owner": tm["owner"],
        "description": tm["description"],
        "version": tm["version"],
        "created_at": tm["created_at"],
        "summary": json.loads(tm["model_json"]),
    }


@v1.get("/threat-model/{model_id}/export/threat-dragon")
async def v1_export_threat_dragon(
    model_id: str,
    current_user: AuthUser = Depends(get_current_user),
) -> dict:
    """Export threat model as OWASP Threat Dragon v2 JSON."""
    from cherenkov.core.storage.database import get_threat_model

    tm = get_threat_model(model_id)
    if not tm:
        raise HTTPException(status_code=404, detail="Threat model not found")
    return json.loads(tm["threat_dragon_json"])


@v1.get("/threat-model/{model_id}/export/tmbom")
async def v1_export_tmbom(
    model_id: str,
    current_user: AuthUser = Depends(get_current_user),
) -> dict:
    """Export threat model as OWASP TM-BOM (CycloneDX ECMA-424 format)."""
    from cherenkov.core.storage.database import get_threat_model

    tm = get_threat_model(model_id)
    if not tm:
        raise HTTPException(status_code=404, detail="Threat model not found")
    return json.loads(tm["tmbom_json"])


@v1.get("/threat-model/{model_id}/export/dfd")
async def v1_export_dfd(
    model_id: str,
    current_user: AuthUser = Depends(get_current_user),
) -> dict:
    """Export threat model DFD as a Mermaid.js flowchart."""
    from cherenkov.core.storage.database import get_threat_model

    tm = get_threat_model(model_id)
    if not tm:
        raise HTTPException(status_code=404, detail="Threat model not found")
    return {
        "format": "mermaid",
        "diagram": tm["mermaid_dfd"],
    }


@v1.get("/threat-model/list")
async def v1_list_threat_models(
    current_user: AuthUser = Depends(get_current_user),
) -> list[dict]:
    """List all stored threat models."""
    from cherenkov.core.storage.database import list_threat_models

    return list_threat_models(20)


# ── Legacy scan + health endpoints (keep for backwards compat) ───────────────


@app.post("/api/scan")
async def scan_target(request: ScanRequest) -> dict:
    """Run all registered scanners against a target URL."""
    return await _run_scan(request)


# ── Health ───────────────────────────────────────────────────────────────────


@app.get("/health")
async def health() -> dict:
    return {"status": "healthy", "agents": "operational", "queue": {"scan_jobs_pending": 0}}


@app.post("/workflows/execute", response_model=WorkflowResponse)
async def execute_workflow(request: WorkflowExecuteRequest) -> WorkflowResponse:
    """Execute a workflow by name or config"""
    try:
        # Load workflow config
        if request.config:
            config = request.config
        else:
            # Sanitize workflow_name before path construction (prevent path traversal)
            safe_name = Path(request.workflow_name).name
            if not re.fullmatch(r"[a-zA-Z0-9_-]+", safe_name):
                raise HTTPException(
                    status_code=400,
                    detail="workflow_name must contain only letters, digits, hyphens, or underscores",
                )
            workflow_path = str(Path("examples/workflows") / f"{safe_name}.yaml")
            config = load_workflow(workflow_path)

        # Execute
        result = orchestrate_workflow(config)

        # Save result
        store = ResultStore()
        store.save_result(request.workflow_name, result.outputs)

        return WorkflowResponse(
            success=result.success,
            workflow=request.workflow_name,
            outputs=result.outputs,
            duration=result.duration,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/workflows")
async def list_workflows() -> dict:
    """List available workflows"""
    from pathlib import Path

    workflows_dir = Path("examples/workflows")
    if workflows_dir.exists():
        workflows = [f.stem for f in workflows_dir.glob("*.yaml")]
        return {"workflows": workflows, "count": len(workflows)}
    return {"workflows": [], "count": 0}


@app.get("/results/{workflow_name}")
async def get_results(workflow_name: str) -> dict:
    """Get latest results for a workflow"""
    store = ResultStore()
    result = store.get_latest(workflow_name)
    if result:
        return result
    raise HTTPException(status_code=404, detail="No results found")


@v1.get("/mesh/nodes")
async def v1_mesh_nodes(current_user: AuthUser = Depends(get_current_user)) -> dict:
    """List discovered mesh nodes."""
    import socket

    from cherenkov.core.mesh import MeshManager

    # Note: In production, this would be a persistent singleton
    manager = MeshManager(node_name=f"node-{socket.gethostname()}")
    nodes = manager.discover_nodes(timeout=1.0)
    manager.shutdown()

    return {"nodes": nodes, "count": len(nodes)}


# Register /api/v1 router
app.include_router(v1)


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("cherenkov_API_HOST", "127.0.0.1")
    port = int(os.getenv("cherenkov_API_PORT", "8000"))
    uvicorn.run(app, host=host, port=port, log_level="info")
