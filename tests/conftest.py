import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.infrastructure.database.models import Base
from src.infrastructure.database.session import DatabaseSession
from src.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    session_factory = async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def test_client(db_engine):
    from src.infrastructure.api import dependencies

    test_db = DatabaseSession.__new__(DatabaseSession)
    test_db._engine = db_engine
    test_db._session_factory = async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    original_get_db = dependencies.get_database_session
    dependencies._db_session = test_db

    async with AsyncClient(
        base_url="http://test",
        transport=ASGITransport(app=app),
    ) as client:
        yield client

    dependencies._db_session = None
