"""Session-based JWT authentication using cookies."""

import jwt
from cherenkov.api.middleware.auth import JWT_SECRET, Role, User
from fastapi import Depends, HTTPException, Request, status

ALGORITHM = "HS256"


async def canonical_get_current_user(request: Request) -> User:
    """Read JWT from session cookie and validate it.

    This is the canonical session-based auth dependency for the web UI.
    Reads the 'session' cookie, validates the JWT, and returns a User.
    """
    token = request.cookies.get("session")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing session cookie",
        )

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role_val: int = payload.get("role")

        if username is None or role_val is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        return User(username=username, role=Role(role_val))

    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


get_current_user_dependency = Depends(canonical_get_current_user)
