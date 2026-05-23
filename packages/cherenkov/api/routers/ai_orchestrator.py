from fastapi import APIRouter

router = APIRouter()

@router.get("/ai/status")
async def ai_status():
    return {"status": "ready"}
