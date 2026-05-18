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
from typing import Any, Dict, List, Literal, Optional, Set
from urllib.parse import urlparse

import httpx
from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    HTTPException,
    Request,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.routing import APIRouter
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

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
from cherenkov.core.storage.database import (
    _DB_PATH,
    erase_target_data,
    get_audit_log,
    get_user,
    save_audit_entry,
)
from cherenkov.core.tokamak import Command, Tokamak
from cherenkov.orchestration.orchestration_api import orchestrate_workflow
from cherenkov.orchestration.result_persistence import ResultStore
from cherenkov.orchestration.workflow_parser import load_workflow

logger = logging.getLogger(__name__)

_STATIC_DIR = Path(__file__).parent / "static"

# Rate limits are intentionally conservative — scanning is CPU/GPU-heavy and
# an unbounded queue would exhaust the local Ollama instance.
_SCAN_RATE = os.getenv("CHERENKOV_SCAN_RATE_LIMIT", "30/minute")
_WORKFLOW_RATE = os.getenv("CHERENKOV_WORKFLOW_RATE_LIMIT", "10/minute")

limiter = Limiter(key_func=get_remote_address)
# Keep _limiter as alias so decorator references below stay consistent
_limiter = limiter

_START_TIME = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    from cherenkov.api.middleware.auth import Role, hash_password
    from cherenkov.core.circuit_breaker import meissner_hub
    from cherenkov.core.storage.database import get_user, init_db, save_user

    # Initialize database
    init_db()

    # Auto-provision default admin user if it doesn't exist
    if not get_user("admin"):
        hashed = hash_password("admin")
        save_user("admin", hashed, Role.ADMIN)

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
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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


class FridaGenerateRequest(BaseModel):
    platform: str
    hooks: List[str]


class AssistantAdviceRequest(BaseModel):
    findings: List[dict]
    context: Optional[dict] = None


@v1.post("/mobile/frida/generate")
async def v1_frida_generate(
    request: FridaGenerateRequest, current_user: AuthUser = Depends(get_current_user)
) -> dict:
    """Generate Frida scripts for mobile runtime analysis."""

    script = f"/* CHERENKOV FRIDA GENERATOR // PLATFORM: {request.platform.upper()} */\n\n"

    if request.platform == "android":
        if "ssl_pinning" in request.hooks:
            script += """
// Android SSL Pinning Bypass (Generic)
Java.perform(function() {
    var array_list = Java.use("java.util.ArrayList");
    var ApiClient = Java.use("com.android.org.conscrypt.TrustManagerImpl");

    ApiClient.checkServerTrusted.implementation = function(chain, authType) {
        return array_list.$new();
    };
});
"""
        if "root_detection" in request.hooks:
            script += """
// Android Root Detection Bypass
Java.perform(function() {
    var RootPackages = ["com.noshufou.android.su", "com.thirdparty.superuser", "eu.chainfire.supersu"];
    var File = Java.use("java.io.File");

    File.exists.implementation = function() {
        var name = this.getName();
        if (RootPackages.indexOf(name) > -1) {
            return false;
        }
        return this.exists();
    };
});
"""
    elif request.platform == "ios":
        if "ssl_pinning" in request.hooks:
            script += """
// iOS SSL Pinning Bypass
if (ObjC.available) {
    for (var className in ObjC.classes) {
        if (className.indexOf("TrustManager") !== -1) {
            // Mocking bypass logic
        }
    }
}
"""

    return {"script": script, "platform": request.platform}


@v1.post("/assistant/advice")
async def v1_assistant_advice(
    request: AssistantAdviceRequest, current_user: AuthUser = Depends(get_current_user)
) -> dict:
    """Get remediation advice from the AI Studio Assistant (Ollama)."""
    import json

    import httpx

    prompt = f"As a security expert, provide concise remediation advice for the following findings:\n{json.dumps(request.findings)}"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Note: _check_ollama must be defined or imported
            ollama_status = await _check_ollama()
            if ollama_status != "ready":
                return {
                    "advice": "AI Studio Assistant is offline (Ollama not detected). Manual remediation recommended.",
                    "status": "offline",
                }

            r = await client.post(
                "http://localhost:11434/api/generate",
                json={"model": "mistral", "prompt": prompt, "stream": False},
            )
            if r.status_code == 200:
                data = r.json()
                return {"advice": data.get("response", ""), "status": "ready"}
            else:
                return {"advice": "Failed to get advice from Ollama.", "status": "error"}
    except Exception as exc:
        return {"advice": f"Assistant error: {exc}", "status": "error"}


@app.post("/api/v1/auth/token")
async def login(credentials: dict):
    if credentials.get("username") == "admin" and credentials.get("password") == "admin":
        return {"access_token": "cherenkov-dev-token", "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")


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


class EraseTargetRequest(BaseModel):
    target: str
    attested_by: str  # name of the operator authorizing erasure
    reason: str = "data_subject_request"


@v1.delete("/data/target")
async def v1_erase_target(
    request: EraseTargetRequest,
    current_user: AuthUser = Depends(RoleChecker(Role.ADMIN)),
) -> dict:
    """Right-to-erasure endpoint (Law 151/2020 Art. 15).

    Nulls all finding payloads for the given target URL and purges
    related audit entries. Returns a signed erasure receipt.
    Requires ADMIN role.
    """
    receipt = await asyncio.to_thread(erase_target_data, request.target)
    receipt["attested_by"] = request.attested_by
    receipt["reason"] = request.reason

    save_audit_entry(
        event_type="DATA_ERASURE",
        user_id=current_user.username,
        details={
            "target": request.target,
            "attested_by": request.attested_by,
            "reason": request.reason,
            "trace_hash": receipt["trace_hash"],
        },
    )
    return receipt


async def _check_ollama() -> str:
    try:
        async with httpx.AsyncClient(timeout=3.0) as c:
            r = await c.get("http://localhost:11434/api/tags")
            return "ready" if r.status_code == 200 else "offline"
    except Exception:
        return "offline"


async def _check_qdrant() -> str:
    try:
        async with httpx.AsyncClient(timeout=2.0) as c:
            r = await c.get("http://localhost:6333/health")
            return "ready" if r.status_code == 200 else "offline"
    except Exception:
        return "offline"


def _get_active_scans_count() -> int:
    try:
        with sqlite3.connect(_DB_PATH) as conn:
            return conn.execute("SELECT count(*) FROM scans WHERE status = 'running'").fetchone()[0]
    except Exception:
        return 0


async def _get_qdrant_vector_count() -> int:
    try:
        async with httpx.AsyncClient(timeout=1.0) as c:
            r = await c.get("http://localhost:6333/collections/cherenkov_findings")
            if r.status_code == 200:
                return r.json().get("result", {}).get("vectors_count", 0) or 0
    except Exception:
        pass
    return 0


def _get_tokamak_container_count() -> int:
    """Return count of running TOKAMAK containers (label=cherenkov.role=tokamak)."""
    try:
        import subprocess

        result = subprocess.run(
            ["docker", "ps", "--filter", "label=cherenkov.role=tokamak", "--format", "{{.ID}}"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        return len([ln for ln in result.stdout.strip().splitlines() if ln])
    except Exception:
        return 0


@v1.get("/health")
async def v1_health() -> dict:
    """Health check used by useMetrics / useQueueDepth hooks.

    Returns the node topology expected by NodeStatusRow and
    the Meissner shield state expected by ForensicHeader.
    """

    from cherenkov.core.storage.database import db_stats

    active_scans = _get_active_scans_count()
    ollama_status, qdrant_status, vector_count, container_count = await asyncio.gather(
        _check_ollama(),
        _check_qdrant(),
        _get_qdrant_vector_count(),
        asyncio.to_thread(_get_tokamak_container_count),
    )

    return {
        "status": "healthy",
        "version": "1.1.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "storage": db_stats(),
        "queue": {"scan_jobs_pending": active_scans},
        "nodes": {
            "tensor": {"status": ollama_status, "model": "Llama 3.1 8B"},
            "kinetic": {"status": ollama_status, "model": "Qwen2.5 3B", "ram_gb": 8},
            "aegis": {"status": ollama_status, "model": "Llama 3.1 8B", "ram_gb": 8},
            "lattice": {
                "status": qdrant_status,
                "model": "Qdrant / Vector",
                "vector_count": vector_count,
            },
            "tokamak": {
                "status": "ready",
                "model": "Sandbox Ready",
                "active_containers": container_count,
            },
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
@limiter.limit(_SCAN_RATE)
async def v1_scan(
    request: Request,
    scan_request: "ScanRequest",
    background_tasks: BackgroundTasks,
    current_user: AuthUser = Depends(get_current_user),
) -> dict:
    """Proxy to the core scan engine; broadcasts a live event on completion.

    Rate-limited to 30 requests/minute per IP to protect Ollama from exhaustion.
    """
    result = await _run_scan(scan_request, background_tasks)

    # Audit log
    save_audit_entry(
        event_type="SCAN_INITIATED",
        user_id=current_user.username,
        details={"target": scan_request.url, "scan_id": result["scan_id"]},
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
async def v1_scan_report_pdf(scan_id: str, current_user: AuthUser = Depends(get_current_user)):
    """Download PDF security report."""
    from fastapi.responses import Response

    from cherenkov.compliance.mapper import ComplianceMapper
    from cherenkov.compliance.reports import PDFReportGenerator
    from cherenkov.core.base_scanner import Finding, ScanResult, Severity
    from cherenkov.core.storage.database import get_scan

    scan = get_scan(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    # Map database scan dict to ScanResult model
    findings = []
    mapper = ComplianceMapper()

    for f in scan.get("findings", []):
        findings.append(
            Finding(
                title=f.get("title", "Unknown"),
                severity=Severity(str(f.get("severity", "INFO")).upper()),
                description=f.get("description", ""),
                cwe=f.get("cwe", ""),
                remediation=f.get("remediation", ""),
            )
        )

    result = ScanResult(
        target=scan.get("target", ""),
        scanner_name="Cherenkov Unified",
        findings=findings,
        status="completed",
    )

    compliance_data = {}
    for f in findings:
        if f.cwe:
            # Flatten the map_all result to list of framework names for simplicity in PDF
            framework_dict = mapper.map_all(f.cwe)
            compliance_data[f.cwe] = list(framework_dict.keys())

    generator = PDFReportGenerator(result, compliance_data)
    pdf_bytes = generator.generate()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=cherenkov_report_{scan_id}.pdf"},
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
    finding_id: str,
    background_tasks: BackgroundTasks,
    current_user: AuthUser = Depends(RoleChecker(Role.OPERATOR)),
) -> dict:
    """Reject a finding (marks it as false positive). Requires OPERATOR role or higher.

    Side-effect: labels the finding in LATTICE so future scans de-rank it
    automatically via cosine similarity scoring.
    """
    from cherenkov.core.lattice_bridge import label_false_positive
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

        # Mark as false positive in LATTICE — runs after response, avoids event-loop leakage
        background_tasks.add_task(label_false_positive, finding_id)

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


_active_scan_targets: set[str] = set()
_active_scan_lock = asyncio.Lock()


async def _run_scan(
    request: "ScanRequest", background_tasks: Optional[BackgroundTasks] = None
) -> dict:
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

    # Deduplication: reject concurrent scans of the same target
    normalised_target = request.url.rstrip("/").lower()
    async with _active_scan_lock:
        if normalised_target in _active_scan_targets:
            raise HTTPException(
                status_code=409,
                detail=f"A scan of '{request.url}' is already in progress. Wait for it to complete.",
            )
        _active_scan_targets.add(normalised_target)

    scan_id = str(uuid.uuid4())
    started = datetime.now(timezone.utc).isoformat()

    try:
        registry = ScannerRegistry()
        engine = ScanEngine(registry)

        async def on_scan_progress(scanner_name: str, result: Any):
            asyncio.get_running_loop().create_task(
                _broadcast({"type": "scan_progress", "scanner": scanner_name})
            )

        scan_results = await engine.scan_all(
            request.url, timeout=10.0, on_progress=on_scan_progress
        )
    except Exception as exc:
        logger.error("ScanEngine failed for %s: %s", request.url, exc)
        async with _active_scan_lock:
            _active_scan_targets.discard(normalised_target)
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

        from cherenkov.core.lattice_bridge import embed_and_store
        from cherenkov.core.storage.database import save_pending_finding

        for v in vulnerabilities:
            finding_id = str(uuid.uuid4())

            # Index every finding in LATTICE for similarity recall and FP learning.
            # Use BackgroundTasks so the work runs after response delivery and
            # doesn't leak asyncio tasks into subsequent test event loops.
            if background_tasks is not None:
                background_tasks.add_task(
                    embed_and_store,
                    finding_id,
                    v["title"],
                    v.get("description", ""),
                    request.url,
                    v["scanner"],
                    v["severity"],
                    v.get("cwe", ""),
                )
            else:
                # Fallback for callers that don't supply background_tasks
                try:
                    asyncio.get_running_loop().create_task(
                        asyncio.to_thread(
                            embed_and_store,
                            finding_id,
                            v["title"],
                            v.get("description", ""),
                            request.url,
                            v["scanner"],
                            v["severity"],
                            v.get("cwe", ""),
                        )
                    )
                except RuntimeError:
                    pass  # No running loop — skip indexing in this context

            if v["severity"] in ("CRITICAL", "HIGH"):
                save_pending_finding(
                    finding_id=finding_id,
                    severity=v["severity"],
                    scanner=v["scanner"],
                    title=v["title"],
                    scan_id=scan_id,
                )
                try:
                    asyncio.get_running_loop().create_task(
                        _broadcast(
                            {
                                "type": "finding_discovered",
                                "finding_id": finding_id,
                                "severity": v["severity"],
                            }
                        )
                    )
                except RuntimeError:
                    pass  # No running loop — skip WebSocket broadcast in this context

    except Exception as exc:
        logger.error("Failed to persist scan %s: %s", scan_id, exc)

    # Trigger SIEM forwarding
    try:
        asyncio.get_running_loop().create_task(_forward_to_siem(vulnerabilities, request.url))
    except RuntimeError:
        pass  # No running loop — skip SIEM forwarding in this context

    result = {
        "scan_id": scan_id,
        "target": request.url,
        "timestamp": finished,
        "vulnerabilities": vulnerabilities,
        "count": len(vulnerabilities),
    }

    # Release dedup lock
    async with _active_scan_lock:
        _active_scan_targets.discard(normalised_target)

    return result


# ── Legacy scan + health endpoints (keep for backwards compat) ───────────────


@app.post("/api/scan")
@limiter.limit(_SCAN_RATE)
async def scan_target(request: Request, scan_request: ScanRequest) -> dict:
    """Run all registered scanners against a target URL."""
    return await _run_scan(scan_request)


# ── Health ───────────────────────────────────────────────────────────────────


@app.get("/health")
async def health() -> dict:
    """Legacy health endpoint — delegates to /api/v1/health for live data."""
    return await v1_health()


@app.post("/workflows/execute", response_model=WorkflowResponse)
@limiter.limit(_WORKFLOW_RATE)
async def execute_workflow(
    http_request: Request, request: WorkflowExecuteRequest
) -> WorkflowResponse:
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


class LatticeQueryRequest(BaseModel):
    title: str
    description: str = ""
    top_k: int = 5
    exclude_false_positives: bool = True


@v1.post("/lattice/similar")
async def v1_lattice_similar(
    request: LatticeQueryRequest,
    current_user: AuthUser = Depends(get_current_user),
) -> dict:
    """
    Query LATTICE for past findings similar to the supplied title + description.

    Used by the dashboard and autonomous agents to surface precedent before
    escalating a new finding.  Excludes false-positives by default.
    """
    from cherenkov.core.lattice_bridge import query_similar_targets

    results = await asyncio.to_thread(
        query_similar_targets,
        request.title,
        request.description,
        request.top_k,
        request.exclude_false_positives,
    )

    return {
        "results": [
            {
                "id": r.id,
                "score": round(r.score, 4),
                "title": r.title,
                "target": r.target,
                "scanner": r.scanner,
                "is_false_positive": r.is_false_positive,
            }
            for r in results
        ],
        "count": len(results),
    }


@v1.get("/lattice/stats")
async def v1_lattice_stats(current_user: AuthUser = Depends(get_current_user)) -> dict:
    """Return LATTICE vector store statistics."""
    from cherenkov.core.lattice_bridge import vector_count

    count = await asyncio.to_thread(vector_count)
    return {
        "vector_count": count,
        "collection": "cherenkov_findings",
        "status": "ready" if count >= 0 else "offline",
    }


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
