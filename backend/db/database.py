from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from backend.core.config import get_settings

#

settings = get_settings()


engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
    echo=settings.debug,
)



class BaseDbModel(DeclarativeBase):
    pass



# https://stackoverflow.com/a/74000761
async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(BaseDbModel.metadata.create_all)



# https://habr.com/ru/articles/1044300/
async def get_db_session() -> AsyncSession: # type: ignore
    async with async_sessionmaker() as session:
        yield session



def now_UTC() -> datetime:
    return datetime.now(UTC)

