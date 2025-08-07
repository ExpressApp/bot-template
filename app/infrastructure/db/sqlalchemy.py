"""SQLAlchemy helpers."""

from asyncio import current_task
from contextlib import asynccontextmanager
from functools import lru_cache, wraps
from typing import Any, Callable

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool.impl import AsyncAdaptedQueuePool

from app.settings import settings

AsyncSessionFactory = Callable[..., AsyncSession]


def make_url_async(url: str) -> str:
    """Add +asyncpg to url scheme."""
    return "postgresql+asyncpg" + url[url.find(":") :]


def make_url_sync(url: str) -> str:
    """Remove +asyncpg from url scheme."""
    return "postgresql" + url[url.find(":") :]


convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

Base = declarative_base(metadata=MetaData(naming_convention=convention))

@lru_cache(maxsize=1)
def get_engine() -> AsyncEngine:
    """Lazily initialize and cache a single SQLAlchemy async engine."""
    return create_async_engine(
        make_url_async(settings.POSTGRES_DSN),
        poolclass=AsyncAdaptedQueuePool,
        pool_size=settings.DB_ENGINE_POOL_SIZE,
        max_overflow=settings.DB_ENGINE_MAX_OVERFLOW,
        pool_recycle=settings.DB_ENGINE_POOL_RECYCLE,
    )


def get_session_factory() -> async_sessionmaker:
    engine = get_engine()
    return async_sessionmaker(bind=engine, expire_on_commit=False)

#
# def provide_session(func: Callable) -> Callable:
#     """
#     Provides a database session to an async function if one is not already passed.
#
#     :param func: The asynchronous function to wrap. It must accept a `session`
#         keyword argument.
#     :return: The wrapped function with automatic session provisioning."""
#
#     @wraps(func)
#     async def wrapper(*args: Any, **kwargs: Any) -> Any:
#         if kwargs.get("session"):
#             return await func(*args, **kwargs)
#
#         async with session_factory() as session:
#             try:
#                 return await func(*args, **kwargs, session=session)
#             except Exception:
#                 await session.rollback()
#                 raise
#             finally:
#                 await session.close()
#
#     return wrapper
