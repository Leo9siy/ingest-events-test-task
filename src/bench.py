import asyncio, time, uuid
from datetime import datetime, timezone, timedelta
import httpx

API = "http://127.0.0.1:8000"
N = 100_000
BATCH = 2000

def make_event(i: int):
    dt = datetime(2025, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=i % 1440)
    return {
        "event_id": str(uuid.uuid4()),
        "occurred_at": dt.isoformat(),
        "user_id": f"user_{i % 20000}",
        "event_type": "click" if i % 2 == 0 else "view",
        "properties": {"i": i},
    }

async def main():
    events = [make_event(i) for i in range(N)]

    async with httpx.AsyncClient(timeout=60) as client:
        t0 = time.perf_counter()
        for i in range(0, N, BATCH):
            r = await client.post(f"{API}/events", json=events[i:i+BATCH])
            r.raise_for_status()
        t1 = time.perf_counter()

        from_ = "2025-01-01"
        to_ = "2025-01-01"
        t2 = time.perf_counter()
        r = await client.get(f"{API}/stats/dau?from={from_}&to={to_}")
        r.raise_for_status()
        t3 = time.perf_counter()

    print(f"Ingest {N}: {t1-t0:.2f}s => {N/(t1-t0):.0f} events/sec")
    print(f"DAU query: {t3-t2:.3f}s, resp={r.json()}")

if __name__ == "__main__":
    asyncio.run(main())
