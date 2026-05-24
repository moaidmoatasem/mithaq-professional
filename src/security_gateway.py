#!/usr/bin/env python3
"""
CHERENKOV — Autonomic Security Gateway Middleware
Provides verified middleware components to secure high-risk endpoints.
Resolves:
  - C4 (No rate limiting on auth endpoint) via sliding-window IP rate limiting.
  - C5 (WebSocket broadcast not authenticated) via JWT query/header validation.
"""

import time
import jwt
import logging
from collections import defaultdict
from typing import Dict, List, Tuple, Optional, Any

logger = logging.getLogger("CherenkovSecurityGateway")


class SlidingWindowRateLimiter:
    """Memory-efficient sliding window rate limiter to protect endpoints from brute-force attacks."""

    def __init__(self, limit: int = 5, window_seconds: float = 60.0):
        self.limit = limit
        self.window_seconds = window_seconds
        # Maps IP string to list of timestamps
        self.requests = defaultdict(list)

    def is_allowed(self, ip_address: str) -> Tuple[bool, int]:
        """Checks if a request from the given IP address is allowed within the rate limits.
        
        Returns:
          Tuple[bool, int] -> (is_allowed_boolean, remaining_allowed_attempts)
        """
        now = time.time()
        ip_requests = self.requests[ip_address]

        # Evict timestamps outside the window
        cutoff = now - self.window_seconds
        while ip_requests and ip_requests[0] < cutoff:
            ip_requests.pop(0)

        # Evaluate attempts
        if len(ip_requests) >= self.limit:
            # Block request, return 0 remaining
            logger.warning(f"[SECURITY ALERT] Rate limit exceeded for IP: {ip_address}")
            return False, 0

        # Log current attempt
        ip_requests.append(now)
        remaining = self.limit - len(ip_requests)
        return True, remaining


class WebSocketAuthenticator:
    """Validates JWT tokens during WebSocket connections to prevent unauthenticated information leaks."""

    def __init__(self, secret_key: str = "Cherenkov-Sovereign-Secret-Key-2026", algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def validate_connection(self, query_string: str, headers: Optional[Dict[str, str]] = None) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Extracts and validates JWT tokens from WebSocket queries or connection headers.
        
        Returns:
          Tuple[bool, Optional[Dict[str, Any]]] -> (is_authenticated, verified_user_payload)
        """
        token = None

        # 1. Try to extract from Authorization connection header
        if headers:
            auth_header = headers.get("authorization", "") or headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header[7:].strip()

        # 2. Fall back to query parameter (typical for WebSocket client libraries)
        if not token and query_string:
            # Parse token from query format "token=eyJhbG..."
            params = dict(param.split("=") for param in query_string.split("&") if "=" in param)
            token = params.get("token")

        if not token:
            logger.warning("[SECURITY ALERT] WebSocket connection rejected: Missing authorization token.")
            return False, None

        # 3. Decode and verify JWT
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            logger.info(f"WebSocket connection authenticated successfully for user: {payload.get('sub', 'unknown')}")
            return True, payload
        except jwt.ExpiredSignatureError:
            logger.warning("[SECURITY ALERT] WebSocket connection rejected: Expired token signature.")
            return False, None
        except jwt.InvalidTokenError as e:
            logger.warning(f"[SECURITY ALERT] WebSocket connection rejected: Invalid token ({e}).")
            return False, None


if __name__ == "__main__":
    print("==========================================================")
    print("      CHERENKOV · SECURITY GATEWAY MIDDLEWARE HARNESS      ")
    print("==========================================================\n")
    
    # 1. Test Sliding Window Rate Limiter
    print("1. Testing Auth Rate Limiter (Limit 3 requests / 5 sec)...")
    limiter = SlidingWindowRateLimiter(limit=3, window_seconds=5.0)
    
    for i in range(1, 6):
        allowed, remaining = limiter.is_allowed("192.168.1.50")
        print(f"   Request {i:<2}: Status={'ALLOWED' if allowed else 'BLOCKED'} | Remaining={remaining}")
        time.sleep(0.5)

    print("\nWaiting for window cooldown...")
    time.sleep(3.5)
    allowed, remaining = limiter.is_allowed("192.168.1.50")
    print(f"   Request 6 : Status={'ALLOWED' if allowed else 'BLOCKED'} (Post Cooldown)")

    # 2. Test WebSocket Authenticator
    print("\n2. Testing WebSocket Authenticator...")
    auth = WebSocketAuthenticator()
    
    # Generate mock token
    payload = {"sub": "moaid", "role": "admin", "exp": time.time() + 10}
    valid_token = jwt.encode(payload, auth.secret_key, algorithm=auth.algorithm)
    
    print("   Validating with valid query token...")
    ok, user = auth.validate_connection(f"token={valid_token}")
    print(f"   Status={'SUCCESS' if ok else 'FAILED'} | User={user.get('sub') if user else None}")

    print("\n   Validating with malicious query token...")
    ok, user = auth.validate_connection("token=invalid_token_xyz")
    print(f"   Status={'SUCCESS' if ok else 'FAILED'}")
    print("===============================================================\n")
