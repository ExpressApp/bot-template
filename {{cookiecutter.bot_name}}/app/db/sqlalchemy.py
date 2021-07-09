"""SQLAlchemy helpers."""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.settings.config import get_app_settings

DATABASE_URL = get_app_settings().DATABASE_URL


def make_url_async(url: str) -> str:
    """Add +asyncpg to url scheme."""
    return "postgresql+asyncpg" + url[url.find(":") :]  # noqa: WPS336


def make_url_sync(url: str) -> str:
    """Add +asyncpg to url scheme."""
    return "postgresql" + url[url.find(":") :]  # noqa: WPS336


Base = declarative_base()


class AsyncDatabaseSession:
    """Database session class."""

    def __init__(self) -> None:
        """Initialize."""
        self._session = None
        self._engine = None

    def __getattr__(self, name: str) -> Any:
        """Get session attrs by default."""
        return getattr(self._session, name)

    async def init(self) -> None:
        """Async initialization."""
        self._engine = create_async_engine(make_url_async(DATABASE_URL), echo=True)

        self._session = sessionmaker(
            self._engine, expire_on_commit=False, class_=AsyncSession
        )()

    async def create_all(self) -> None:
        """Create database schema."""
        assert self._engine is not None
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close(self) -> None:
        """Close session."""
        assert self._session is not None
        await self._session.close()


async_db_session = AsyncDatabaseSession()
