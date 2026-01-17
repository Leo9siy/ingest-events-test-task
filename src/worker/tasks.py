from celery import shared_task
from sqlalchemy.dialects.postgresql import insert
from src.database.connection import get_context_session
from src.database.models import EventModel

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5})
def ingest_events_task(self, rows: list[dict]):
    # Celery task sync, но внутри можем открыть async loop, либо сделать sync engine.
    # Проще: отдельный sync engine для воркера (или использовать anyio).
    import asyncio

    async def run():
        async with get_context_session() as session:
            stmt = insert(EventModel).values(rows).on_conflict_do_nothing(index_elements=["event_id"])
            await session.execute(stmt)
            await session.commit()

    asyncio.run(run())
