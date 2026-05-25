"""CSRF protection via double-submit cookie pattern."""
from dataclasses import dataclass

from starlette.requests import Request


@dataclass
class CsrfTokenPair:
    """Container for CSRF token cookie and header values."""
    cookie_value: str
    header_value: str


class CsrfError(RuntimeError):
    """Raised when CSRF validation fails."""
    pass


def validate_double_submit(request: Request) -> CsrfTokenPair:
    """Validate the double-submit CSRF token.

    Checks that:
    1. csrf_token cookie exists
    2. X-CSRF-Token header matches the cookie value

    Returns:
        CsrfTokenPair with both values if valid

    Raises:
        CsrfError: If validation fails
    """
    cookie_token = request.cookies.get("csrf_token")
    header_token = request.headers.get("X-CSRF-Token")

    if not cookie_token:
        raise CsrfError("Missing csrf_token cookie")

    if not header_token:
        raise CsrfError("Missing X-CSRF-Token header")

    if cookie_token != header_token:
        raise CsrfError("CSRF token mismatch")

    return CsrfTokenPair(cookie_value=cookie_token, header_value=header_token)