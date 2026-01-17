import uuid
from datetime import datetime, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy import delete, text

from src.database.connection import session_with_rollback, get_context_session, engine
from src.database.models import EventModel
from src.main import app


def dau_for(body, day: str) -> int:
    for row in body["dau"]:
        if row.get("date") == day:
            return row["dau"]
    return 0

@pytest.mark.asyncio
async def test_ingest_then_dau(client):
    today = datetime.now(timezone.utc).date().isoformat()

    r = await client.get(f"/stats/dau/?from={today}&to={today}")
    assert r.status_code == 200, r.text
    first_size = dau_for(r.json(), today)

    events = [
        {
            "event_id": str(uuid.uuid4()),
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            "user_id": "u1",
            "event_type": "click",
            "properties": {"key": "value"},
        },
        {
            "event_id": str(uuid.uuid4()),
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            "user_id": "u2",
            "event_type": "view",
            "properties": {"key": "value"},
        },
    ]

    r = await client.post("/events/", json=events)
    assert r.status_code == 200, r.text

    r = await client.get(f"/stats/dau/?from={today}&to={today}")
    assert r.status_code == 200, r.text
    size = dau_for(r.json(), today)

    assert size - first_size == 2
