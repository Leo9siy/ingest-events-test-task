import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from src.database.connection import get_context_session, session_with_rollback
from src.main import app


@pytest_asyncio.fixture(scope="function")
async def async_session():
    async with session_with_rollback() as session:
        yield session



@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
