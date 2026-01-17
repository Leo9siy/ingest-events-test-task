from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.config import settings
from src.database.models import Base


engine = create_async_engine(
    url=settings.async_url,
    echo=False
)

session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_session():
    await populate()

    async with session_maker() as session:
        yield session


@asynccontextmanager
async def get_context_session():
    #await populate()

    async with session_maker() as session:
        yield session


async def populate():
    async with engine.begin() as connect:
        await connect.run_sync(Base.metadata.create_all)

    print("Successful populated")


@asynccontextmanager
async def session_with_rollback():
    async with session_maker() as session:
        async with session.begin():
            yield session
            await session.rollback()
