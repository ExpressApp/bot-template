"""SQLAlchemy helpers."""

from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.settings.config import get_app_settings

POSTGRES_DSN = get_app_settings().POSTGRES_DSN
SQL_DEBUG = get_app_settings().SQL_DEBUG
AsyncSessionFactory = Callable[..., AsyncSession]


def make_url_async(url: str) -> str:
    """Add +asyncpg to url scheme."""
    return "postgresql+asyncpg" + url[url.find(":") :]  # noqa: WPS336


def make_url_sync(url: str) -> str:
    """Remove +asyncpg from url scheme."""
    return "postgresql" + url[url.find(":") :]  # noqa: WPS336


Base = declarative_base()


def build_db_session_factory() -> AsyncSessionFactory:
    engine = create_async_engine(make_url_async(POSTGRES_DSN), echo=SQL_DEBUG)
    return sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
