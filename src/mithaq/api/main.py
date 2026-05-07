"""
mithaq REST API Server
FastAPI-based API for remote workflow execution
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import sys

sys.path.insert(0, "../..")

from mithaq.orchestration_api import orchestrate_workflow
from mithaq.workflow_parser import load_workflow
from mithaq.result_persistence import ResultStore

app = FastAPI(
    title="mithaq Autonomous Agent API",
    description="REST API for workflow orchestration and security testing",
    version="1.0.0",
)

_ALLOWED_ORIGINS = os.getenv(
    "mithaq_CORS_ORIGINS",
    "http://localhost:5000,http://127.0.0.1:5000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)


# Models
class WorkflowExecuteRequest(BaseModel):
    workflow_name: str
    config: Optional[Dict[str, Any]] = None


class WorkflowResponse(BaseModel):
    success: bool
    workflow: str
    outputs: Dict[str, Any]
    duration: float


# Routes
@app.get("/")
async def root():
    return {
        "message": "mithaq Autonomous Agent API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "workflows": "/workflows",
            "execute": "/workflows/execute",
            "results": "/results",
        },
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "agents": "operational"}


@app.post("/workflows/execute", response_model=WorkflowResponse)
async def execute_workflow(request: WorkflowExecuteRequest):
    """Execute a workflow by name or config"""
    try:
        # Load workflow config
        if request.config:
            config = request.config
        else:
            # Load from examples
            workflow_path = f"examples/workflows/{request.workflow_name}.yaml"
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
async def list_workflows():
    """List available workflows"""
    from pathlib import Path

    workflows_dir = Path("examples/workflows")
    if workflows_dir.exists():
        workflows = [f.stem for f in workflows_dir.glob("*.yaml")]
        return {"workflows": workflows, "count": len(workflows)}
    return {"workflows": [], "count": 0}


@app.get("/results/{workflow_name}")
async def get_results(workflow_name: str):
    """Get latest results for a workflow"""
    store = ResultStore()
    result = store.get_latest(workflow_name)
    if result:
        return result
    raise HTTPException(status_code=404, detail="No results found")


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("mithaq_API_HOST", "127.0.0.1")
    port = int(os.getenv("mithaq_API_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)

