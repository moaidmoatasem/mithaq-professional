from fastapi import HTTPException, Request

from cherenkov.credentials import DefaultCredentialsManager


async def require_rotated_credentials(request: Request) -> Request:
    if DefaultCredentialsManager.is_rotation_required():
        raise HTTPException(
            status_code=423,
            detail={"code": "rotation_required", "message": "Password rotation required"},
        )
    return request
