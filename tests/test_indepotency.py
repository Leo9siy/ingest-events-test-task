import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import select, func

from src.database.models import EventModel
from src.services import EventService
from src.schemas import EventIn

@pytest.mark.asyncio
async def test_ingest_idempotent(async_session):
    svc = EventService(async_session)

    eid = str(uuid.uuid4())
    payload = EventIn(
        event_id=eid,
        occurred_at=datetime.now(timezone.utc),
        user_id="u1",
        event_type="click",
        properties={"a": 1},
    )

    await svc.ingest([payload, payload])  # дубль в одном запросе
    await svc.ingest([payload])           # дубль вторым запросом

    res = await async_session.execute(
        select(func.count()).select_from(EventModel).where(EventModel.event_id == eid)
    )
    assert res.scalar_one() == 1
