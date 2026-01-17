import uuid
from datetime import datetime, timezone

import pytest
from httpx import AsyncClient
from src.main import app


@pytest.mark.asyncio
async def test_ingest_then_dau(async_session, override_db_dependency):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        today = datetime.now(timezone.utc).date().isoformat()

        events = [
            {
                "event_id": str(uuid.uuid4()),
                "occurred_at": datetime.now(timezone.utc).isoformat(),
                "user_id": "u1",
                "event_type": "click",
                "properties": {},
            },
            {
                "event_id": str(uuid.uuid4()),
                "occurred_at": datetime.now(timezone.utc).isoformat(),
                "user_id": "u2",
                "event_type": "view",
                "properties": {},
            },
        ]
        r = await ac.post("/events", json=events)
        assert r.status_code == 200

        r = await ac.get(f"/stats/dau?from={today}&to={today}")
        assert r.status_code == 200
        body = r.json()
        # если ты возвращаешь по дням списком:
        assert body["dau"][0]["dau"] == 2
