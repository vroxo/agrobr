from collections.abc import AsyncGenerator
from functools import lru_cache
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.use_cases.calculate_premium_use_case import CalculatePremiumUseCase
from src.application.use_cases.get_quotes_use_case import GetQuotesUseCase
from src.infrastructure.config.settings import Settings
from src.infrastructure.database.quote_repository import SqlAlchemyQuoteRepository
from src.infrastructure.database.session import DatabaseSession
from src.infrastructure.gis.gis_adapter import SimpleGisAdapter

_db_session: Optional[DatabaseSession] = None


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_database_session() -> DatabaseSession:
    global _db_session
    if _db_session is None:
        settings = get_settings()
        _db_session = DatabaseSession(settings.database_url)
    return _db_session


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    db = get_database_session()
    session = db.get_session()
    try:
        yield session
    finally:
        await session.close()


async def get_calculate_use_case(
    session: AsyncSession,
) -> CalculatePremiumUseCase:
    settings = get_settings()
    gis_adapter = SimpleGisAdapter() if settings.gis_enabled else None
    repository = SqlAlchemyQuoteRepository(session)
    return CalculatePremiumUseCase(
        config=settings,
        gis_adapter=gis_adapter,
        repository=repository,
    )


async def get_quotes_use_case(
    session: AsyncSession,
) -> GetQuotesUseCase:
    repository = SqlAlchemyQuoteRepository(session)
    return GetQuotesUseCase(repository=repository)
