import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import select, func

from src.database.models import EventModel


@pytest.mark.asyncio
async def test_ingest_idempotent(async_session, client):
    eid = str(uuid.uuid4())

    payload = [{
        "event_id": eid,
        "occurred_at": str(datetime.now(timezone.utc).isoformat()),
        "user_id": "user1",
        "event_type": "purchase",
        "properties": {"key": "value"},
    }]

    response = await client.post("/events/", json=payload)
    assert response.status_code == 200

    response = await client.post("/events/", json=payload)
    assert response.status_code == 200

    res = await async_session.execute(
        select(func.count())
        .select_from(EventModel)
        .where(EventModel.event_id == eid)
    )

    assert res.scalar_one() == 1
