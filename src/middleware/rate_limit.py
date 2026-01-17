import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

class TokenBucket:
    def __init__(self, rate: float, capacity: int):
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.updated = time.monotonic()

    def allow(self, cost=1) -> bool:
        now = time.monotonic()
        self.tokens = min(self.capacity, self.tokens + (now - self.updated) * self.rate)
        self.updated = now
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, rate=10.0, capacity=20):
        super().__init__(app)
        self.rate = rate
        self.capacity = capacity
        self.buckets = {}

    async def dispatch(self, request: Request, call_next):
        ip = request.client.host if request.client else "unknown"
        b = self.buckets.get(ip)
        if b is None:
            b = self.buckets[ip] = TokenBucket(self.rate, self.capacity)

        if not b.allow():
            return JSONResponse({"detail": "rate limit exceeded"}, status_code=429)

        return await call_next(request)
