import pytest
from sqlalchemy import text


@pytest.mark.asyncio
async def test_events_indexes_exist(async_session):
    q = text("""
        SELECT indexname
        FROM pg_indexes
        WHERE tablename = 'events';
    """)
    res = await async_session.execute(q)
    indexes = {r[0] for r in res.all()}

    assert any("occurred_at" in i for i in indexes)
    assert any("user_id" in i for i in indexes)
