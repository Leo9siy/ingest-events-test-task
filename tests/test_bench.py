import time
import uuid
from datetime import datetime

import pytest


@pytest.mark.asyncio
async def test_benchmark(client):
    events = [
        {
            "event_id": f"{str(uuid.uuid4())}",
            "occurred_at": str(datetime.now().isoformat()),
            "user_id": f"user{i}",
            "event_type": "purchase",
            "properties": {"key": "value"}
        }
        for i in range(1000)
    ]

    start_time = time.time()
    response = await client.post("/events/", json=events)
    end_time = time.time()

    print(f"Processed 100k events in {end_time - start_time} seconds")

    assert response.status_code == 200
