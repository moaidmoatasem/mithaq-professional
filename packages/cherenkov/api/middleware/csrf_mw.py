"""Starlette middleware for CSRF protection."""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from .csrf import CsrfError, validate_double_submit


class CsrfMiddleware(BaseHTTPMiddleware):
    """Starlette middleware for double-submit CSRF protection."""

    EXEMPT_PATHS = {"/auth/login", "/auth/logout", "/auth/rotate-password", "/health"}
    SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}

    async def dispatch(self, request: Request, call_next):
        if request.method in self.SAFE_METHODS:
            return await call_next(request)

        path = request.url.path
        if any(path == exempt or path.startswith(exempt + "/") for exempt in self.EXEMPT_PATHS):
            return await call_next(request)

        if path.startswith("/api/v1/"):
            try:
                validate_double_submit(request)
            except CsrfError:
                from fastapi import HTTPException

                raise HTTPException(status_code=403, detail="CSRF validation failed")

        return await call_next(request)