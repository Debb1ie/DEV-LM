from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from collections import defaultdict
from typing import Dict, List
import time

from config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Sliding window rate limiter keyed by IP address.
    Chat endpoints get a stricter separate limit.
    """

    def __init__(self, app):
        super().__init__(app)
        # { ip: [timestamp, ...] }
        self._general: Dict[str, List[float]] = defaultdict(list)
        self._chat:    Dict[str, List[float]] = defaultdict(list)

    def _check(
        self,
        store: Dict[str, List[float]],
        key: str,
        limit: int,
        window: int,
    ) -> tuple[bool, int]:
        """Returns (allowed, retry_after_seconds)."""
        now = time.time()
        cutoff = now - window
        timestamps = store[key]

        # Evict old entries
        store[key] = [t for t in timestamps if t > cutoff]

        if len(store[key]) >= limit:
            oldest = store[key][0]
            retry_after = int(oldest + window - now) + 1
            return False, retry_after

        store[key].append(now)
        return True, 0

    async def dispatch(self, request: Request, call_next):
        ip = request.client.host if request.client else "unknown"
        path = request.url.path

        # Stricter limit for AI chat endpoints
        if path.startswith("/api/chat"):
            allowed, retry_after = self._check(
                self._chat, ip,
                settings.CHAT_RATE_LIMIT_REQUESTS,
                settings.CHAT_RATE_LIMIT_WINDOW_SECONDS,
            )
        else:
            allowed, retry_after = self._check(
                self._general, ip,
                settings.RATE_LIMIT_REQUESTS,
                settings.RATE_LIMIT_WINDOW_SECONDS,
            )

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests",
                    "retry_after": retry_after,
                },
                headers={"Retry-After": str(retry_after)},
            )

        response: Response = await call_next(request)
        return response
