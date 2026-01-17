import time
from typing import Annotated

from fastapi import APIRouter, Depends

from src.services import EventService, get_test_event_service


bench_router = APIRouter()
service_dep = Annotated[EventService, Depends(get_test_event_service)]


@bench_router.post(
    path="/benchmark/"
)
async def benchmark(
    service: service_dep,
    from_date: str = "2020-01-01",
    to_date: str = "2025-12-30"
):
    start_time = time.time()

    await service.get_uniq_users_by_date(from_date, to_date)

    processing_time = time.time() - start_time
    return {"processing_time": processing_time}
