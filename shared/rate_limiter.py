"""
shared/rate_limiter.py
──────────────────────
Sliding-window in-memory rate limiter for FastAPI services.
Provides per-IP and per-user-key request throttling without
requiring Redis in development/testing environments.

Usage:
    from shared.rate_limiter import RateLimiter, rate_limit_dependency

    limiter = RateLimiter(max_requests=20, window_seconds=60)

    @app.post("/auth/login")
    async def login(req: Request, _=Depends(limiter.dependency)):
        ...
"""
import time
import threading
from collections import defaultdict, deque
from typing import Callable, Optional

from fastapi import Request, HTTPException, status


class RateLimiter:
    """
    Sliding-window rate limiter.

    Parameters
    ----------
    max_requests : int
        Maximum number of requests allowed per `window_seconds`.
    window_seconds : int
        Length of the sliding window in seconds.
    key_func : callable, optional
        Function that extracts a string key from a ``Request`` object.
        Defaults to client IP address.
    error_message : str, optional
        Detail string returned in the 429 response.
    """

    def __init__(
        self,
        max_requests: int = 30,
        window_seconds: int = 60,
        key_func: Optional[Callable[[Request], str]] = None,
        error_message: str = "Too many requests. Please try again later.",
    ):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.key_func = key_func or self._default_key
        self.error_message = error_message
        self._lock = threading.Lock()
        self._windows: dict[str, deque] = defaultdict(deque)

    @staticmethod
    def _default_key(request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def is_allowed(self, key: str) -> bool:
        """Return True if the key is within rate limits, False otherwise."""
        now = time.monotonic()
        cutoff = now - self.window_seconds
        with self._lock:
            dq = self._windows[key]
            # Evict timestamps outside the window
            while dq and dq[0] < cutoff:
                dq.popleft()
            if len(dq) >= self.max_requests:
                return False
            dq.append(now)
            return True

    def remaining(self, key: str) -> int:
        """Return how many requests are still allowed in the current window."""
        now = time.monotonic()
        cutoff = now - self.window_seconds
        with self._lock:
            dq = self._windows[key]
            count = sum(1 for t in dq if t >= cutoff)
            return max(0, self.max_requests - count)

    async def dependency(self, request: Request) -> None:
        """FastAPI dependency — raises HTTP 429 when limit is exceeded."""
        key = self.key_func(request)
        if not self.is_allowed(key):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=self.error_message,
                headers={"Retry-After": str(self.window_seconds)},
            )


# ── Pre-configured limiters for common use-cases ──────────────────────────────

# Strict: login / register endpoints (5 per minute per IP)
auth_limiter = RateLimiter(
    max_requests=5,
    window_seconds=60,
    error_message="Too many authentication attempts. Please wait 60 seconds.",
)

# Moderate: triage / AI inference endpoints (30 per minute per IP)
ai_limiter = RateLimiter(
    max_requests=30,
    window_seconds=60,
    error_message="AI triage rate limit reached. Please wait before retrying.",
)

# Relaxed: general read endpoints (120 per minute per IP)
api_limiter = RateLimiter(
    max_requests=120,
    window_seconds=60,
    error_message="API rate limit exceeded. Please slow down your requests.",
)
