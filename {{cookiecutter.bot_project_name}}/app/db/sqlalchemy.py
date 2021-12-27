"""SQLAlchemy helpers."""

from typing import Callable

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.settings import settings

AsyncSessionFactory = Callable[..., AsyncSession]


def make_url_async(url: str) -> str:
    """Add +asyncpg to url scheme."""
    return "postgresql+asyncpg" + url[url.find(":") :]  # noqa: WPS336


def make_url_sync(url: str) -> str:
    """Remove +asyncpg from url scheme."""
    return "postgresql" + url[url.find(":") :]  # noqa: WPS336


Base = declarative_base()


async def build_db_session_factory() -> AsyncSessionFactory:
    engine = create_async_engine(
        make_url_async(settings.POSTGRES_DSN),
        echo=settings.SQL_DEBUG,
    )

    await verify_db_connection(engine)

    return sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


async def verify_db_connection(engine: AsyncEngine) -> None:
    connection = await engine.connect()
    await connection.close()
