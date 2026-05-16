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
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.routing import APIRouter
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from cherenkov.core.storage.database import _DB_PATH
from cherenkov.orchestration.orchestration_api import orchestrate_workflow
from cherenkov.orchestration.result_persistence import ResultStore
from cherenkov.orchestration.workflow_parser import load_workflow

logger = logging.getLogger(__name__)

_STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    from cherenkov.core.circuit_breaker import meissner_hub

    meissner_hub.on_open(
        lambda: asyncio.create_task(
            _broadcast({"type": "circuit_breaker", "state": "OPEN", "reason": "threshold_exceeded"})
        )
    )
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
async def v1_sandbox_execute(request: SandboxExecuteRequest) -> dict:
    """Execute a payload in the Tokamak sandbox."""
    import asyncio

    from cherenkov.core.tokamak import Command, Tokamak

    cmd = Command(payload=request.payload, timeout=request.timeout)

    # Run synchronously in an executor to avoid blocking the loop
    result = await asyncio.to_thread(Tokamak.execute, cmd)

    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "trace_hash": result.trace_hash,
        "shred_receipt": result.shred_receipt,
        "exit_code": result.exit_code,
    }


@v1.get("/sandbox/status")
async def v1_sandbox_status() -> dict:
    """Return the status of the Tokamak sandbox."""
    return {"status": "ready"}


@v1.post("/scan")
async def v1_scan(request: "ScanRequest") -> dict:
    """Proxy to the core scan engine; broadcasts a live event on completion."""
    result = await _run_scan(request)
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
async def v1_approve_finding(finding_id: str, operator_id: Optional[str] = None) -> dict:
    """Approve a finding."""
    from cherenkov.core.storage.database import init_db, update_finding_status

    try:
        init_db()
        update_finding_status(finding_id, "approved", operator_id)
        return {"status": "success", "finding_id": finding_id, "new_status": "approved"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to approve finding: {exc}") from exc


@v1.post("/findings/{finding_id}/reject")
async def v1_reject_finding(finding_id: str, operator_id: Optional[str] = None) -> dict:
    """Reject a finding."""
    from cherenkov.core.storage.database import init_db, update_finding_status

    try:
        init_db()
        update_finding_status(finding_id, "rejected", operator_id)
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

    try:
        registry = ScannerRegistry()
        engine = ScanEngine(registry)
        scan_results = await engine.scan_all(request.url, timeout=10.0)
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

    except Exception as exc:
        logger.error("Failed to persist scan %s: %s", scan_id, exc)

    return {
        "scan_id": scan_id,
        "target": request.url,
        "timestamp": finished,
        "vulnerabilities": vulnerabilities,
        "count": len(vulnerabilities),
    }


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


# Register /api/v1 router
app.include_router(v1)


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("cherenkov_API_HOST", "127.0.0.1")
    port = int(os.getenv("cherenkov_API_PORT", "8000"))
    uvicorn.run(app, host=host, port=port, log_level="info")
