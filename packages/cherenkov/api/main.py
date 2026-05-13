"""
cherenkov REST API Server
FastAPI-based API for security scanning, workflow orchestration, and the web dashboard.

Flask has been retired. The dashboard is now served as static HTML from
packages/cherenkov/api/static/index.html via FastAPI StaticFiles.
"""

import logging
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from cherenkov.orchestration.orchestration_api import orchestrate_workflow
from cherenkov.orchestration.result_persistence import ResultStore
from cherenkov.orchestration.workflow_parser import load_workflow

logger = logging.getLogger(__name__)

_STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(
    title="cherenkov Sovereign Security API",
    description="Scan API, workflow orchestration, and web dashboard. Flask retired.",
    version="1.1.0",
)

_ALLOWED_ORIGINS = os.getenv(
    "cherenkov_CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

# Serve the static dashboard assets
if _STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")


# ── Models ──────────────────────────────────────────────────────────────────


class ScanRequest(BaseModel):
    url: str


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


# ── Scan API (replaces cherenkov_web.py Flask /api/scan) ────────────────────


@app.post("/api/scan")
async def scan_target(request: ScanRequest) -> dict:
    """Run all registered scanners against a target URL."""
    from cherenkov.core.engine import ScanEngine
    from cherenkov.core.registry import ScannerRegistry
    from cherenkov.core.storage.database import init_db, save_scan

    # Validate URL before any network activity
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

    # Flatten findings for response and persistence
    vulnerabilities: list[dict] = []
    for scanner_name, result in scan_results.items():
        for f in result.findings:
            vulnerabilities.append(
                {
                    "scanner": scanner_name,
                    "title": f.title,
                    "type": f.title,  # dashboard compatibility
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
    except Exception as exc:
        # Non-fatal: log but still return the result
        logger.error("Failed to persist scan %s: %s", scan_id, exc)

    return {
        "scan_id": scan_id,
        "target": request.url,
        "timestamp": finished,
        "vulnerabilities": vulnerabilities,
        "count": len(vulnerabilities),
    }


# ── Health ───────────────────────────────────────────────────────────────────


@app.get("/health")
async def health() -> dict:
    return {"status": "healthy", "agents": "operational"}


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
        raise HTTPException(status_code=500, detail=str(e))


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


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("cherenkov_API_HOST", "127.0.0.1")
    port = int(os.getenv("cherenkov_API_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
