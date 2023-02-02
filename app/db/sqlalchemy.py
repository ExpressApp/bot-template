"""SQLAlchemy helpers."""

from asyncio import current_task
from typing import Callable

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool.impl import AsyncAdaptedQueuePool

from app.settings import settings

AsyncSessionFactory = Callable[..., AsyncSession]


def make_url_async(url: str) -> str:
    """Add +asyncpg to url scheme."""
    return "postgresql+asyncpg" + url[url.find(":") :]  # noqa: WPS336


def make_url_sync(url: str) -> str:
    """Remove +asyncpg from url scheme."""
    return "postgresql" + url[url.find(":") :]  # noqa: WPS336


Base = declarative_base()

engine: AsyncEngine = create_async_engine(
    make_url_async(settings.POSTGRES_DSN), poolclass=AsyncAdaptedQueuePool
)


async def build_db_session_factory() -> AsyncSessionFactory:
    await verify_db_connection(engine)
    return async_scoped_session(
        sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession),
        scopefunc=current_task,
    )


async def verify_db_connection(engine: AsyncEngine) -> None:
    connection = await engine.connect()
    await connection.close()


async def close_db_connections() -> None:
    await engine.dispose()
