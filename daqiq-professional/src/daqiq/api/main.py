"""
DAQIQ REST API Server
FastAPI-based API for remote workflow execution
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import sys

sys.path.insert(0, "../..")

from daqiq.orchestration_api import orchestrate_workflow
from daqiq.workflow_parser import load_workflow
from daqiq.result_persistence import ResultStore

app = FastAPI(
    title="DAQIQ Autonomous Agent API",
    description="REST API for workflow orchestration and security testing",
    version="1.0.0",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
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
        "message": "DAQIQ Autonomous Agent API",
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

    uvicorn.run(app, host="0.0.0.0", port=8000)
