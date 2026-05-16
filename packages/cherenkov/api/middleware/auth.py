from datetime import datetime, timedelta, timezone
from enum import IntEnum
from typing import Annotated, Optional

import bcrypt
import jwt
from fastapi import Depends, Header, HTTPException, status
from pydantic import BaseModel

# Security Constants (In a real app, these should be in .env)
JWT_SECRET = "cherenkov-sovereign-audit-key-2024"  # Placeholder
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


class Role(IntEnum):
    ADMIN = 3
    ANALYST = 2
    OPERATOR = 1
    GUEST = 0


class User(BaseModel):
    username: str
    role: Role


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(authorization: Annotated[Optional[str], Header()] = None) -> User:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
            )

        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role_val: int = payload.get("role")

        if username is None or role_val is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        return User(username=username, role=Role(role_val))

    except (jwt.PyJWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


class RoleChecker:
    def __init__(self, required_role: Role):
        self.required_role = required_role

    def __call__(self, user: User = Depends(get_current_user)):
        if user.role < self.required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires {self.required_role.name} privileges or higher",
            )
        return user


# Helper for bcrypt
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
