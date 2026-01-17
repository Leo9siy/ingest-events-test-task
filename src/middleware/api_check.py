from fastapi import HTTPException
from httpx import Request
from starlette.middleware.base import BaseHTTPMiddleware


class APIKeyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, api_key: str):
        super().__init__(app)
        self.api_key = api_key

    async def dispatch(self, request: Request, call_next):
        api_key = request.headers.get("X-API-KEY")
        if api_key != self.api_key:
            raise HTTPException(status_code=403, detail="Forbidden")
        return await call_next(request)
