import pytest_asyncio

from src.database.connection import get_context_session


@pytest_asyncio.fixture
async def async_session():
    async with get_context_session() as session:
        yield session

