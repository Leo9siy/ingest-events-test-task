import structlog

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from src.middleware.api_check import APIKeyMiddleware
from src.middleware.rate_limit import RateLimitMiddleware
from src.routers.benchmark import bench_router
from src.routers.routers import router


app = FastAPI()
app.include_router(router=router)
app.include_router(router=bench_router)


instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)


log = structlog.get_logger()


@app.middleware("http")
async def log_requests(request, call_next):
    resp = await call_next(request)
    log.info("request",
             method=request.method,
             path=request.url.path,
             status=resp.status_code
             )
    return resp


app.add_middleware(RateLimitMiddleware, rate=20.0, capacity=40)
#app.add_middleware(APIKeyMiddleware, "Bearer")
