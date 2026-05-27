"""
C2 Hub Router - API endpoints for agent coordination and control tower.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from cherenkov.api.middleware.auth import Role, RoleChecker, User, get_current_user
from cherenkov.core.c2_hub import default_c2_hub

router = APIRouter(prefix="/c2", tags=["C2 Hub"])
hub = default_c2_hub()

class HandoverRequest(BaseModel):
    source_agent_id: str
    target_agent_id: str
    reason: str

class HandoverCompleteRequest(BaseModel):
    snapshot_id: str

class AssumeRoleRequest(BaseModel):
    agent_id: str

@router.get("/status")
async def get_c2_status(current_user: User = Depends(get_current_user)):
    """Get the current status of the C2 Hub Control Tower."""
    return hub.get_hub_status()

@router.get("/ssot")
async def get_ssot(current_user: User = Depends(get_current_user)):
    """Get the content of the Single Source of Truth."""
    return {"content": hub.get_ssot_content()}

@router.post("/assume-role")
async def assume_c2_role(request: AssumeRoleRequest, current_user: User = Depends(RoleChecker(Role.ADMIN))):
    """Set an agent as the active C2 coordinator. Requires ADMIN role."""
    success = hub.assume_c2_role(request.agent_id)
    if not success:
        raise HTTPException(status_code=400, detail=f"Failed to assume C2 role for agent {request.agent_id}")
    return {"status": "success", "active_c2_agent": request.agent_id}

@router.post("/handover/initiate")
async def initiate_handover(request: HandoverRequest, current_user: User = Depends(RoleChecker(Role.OPERATOR))):
    """Initiate a formal handover between agents. Requires OPERATOR role."""
    snapshot_id = hub.initiate_handover(request.source_agent_id, request.target_agent_id, request.reason)
    if not snapshot_id:
        raise HTTPException(status_code=400, detail="Handover initiation failed")
    return {"status": "initiated", "snapshot_id": snapshot_id}

@router.post("/handover/complete")
async def complete_handover(request: HandoverCompleteRequest, current_user: User = Depends(RoleChecker(Role.OPERATOR))):
    """Complete a pending handover. Requires OPERATOR role."""
    success = hub.complete_handover(request.snapshot_id)
    if not success:
        raise HTTPException(status_code=400, detail="Handover completion failed")
    return {"status": "completed"}
