import uuid

import pytest


@pytest.mark.asyncio
async def test_ingest_events(client):
    response = await client.post("/events/", json=[{
        "event_id": f"{str(uuid.uuid4())}",
        "occurred_at": "2026-01-16T00:00:00",
        "user_id": "user1",
        "event_type": "purchase",
        "properties": {}
    }])
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_dau(client):
    response = await client.get("/stats/dau/?from=2026-01-01&to=2026-01-16")
    assert response.status_code == 200
    assert "dau" in response.json()



