from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from src.middleware.rate_limit import RateLimitMiddleware
from src.routers import router


app = FastAPI()
app.include_router(router=router)


instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

import structlog
log = structlog.get_logger()

@app.middleware("http")
async def log_requests(request, call_next):
    resp = await call_next(request)
    log.info("request",
             method=request.method,
             path=request.url.path,
             status=resp.status_code)
    return resp


app.add_middleware(RateLimitMiddleware, rate=20.0, capacity=40)
