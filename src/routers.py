from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.schemas import EventIn
from src.services import EventService, get_event_service


router = APIRouter()
service_dep = Annotated[EventService, Depends(get_event_service)]


@router.post(
    path="/events/",
    summary="Ingest events"
)
async def ingest_events(
        events: list[EventIn],
        service: service_dep
):
    return await service.ingest(events)

#/stats/dau?from=YYYY-MM-DD&to=YYYY-MM-DD
@router.get(
    path="/stats/dau/",
    summary="Get count of unique Users by days"
)
async def get_dau(
        to: str,
        service: service_dep,
        from_: str = Query(..., alias="from"),
):
    return await service.get_uniq_users_by_date(from_, to)

# /stats/top-events?from&to&limit=10
@router.get(
    path="/stats/top-events",
    summary="Get TOP events"
)
async def get_top(
    service: service_dep,
    to: str,
    limit: int = 10,
    from_: str = Query(..., alias="from"),
):
    return await service.get_top_events(from_, to, limit)

# /stats/retention?start_date=YYYY-MM-DD&windows=3
@router.get(
    path="/stats/retention/",
    summary="Get retention"
)
async def get_retention(
        start_date: str,
        windows: int,
        service: service_dep,
):
    return await service.get_retention(start_date, windows)
