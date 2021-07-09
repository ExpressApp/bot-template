"""Database models declarations."""

from typing import Any

from sqlalchemy import Column, Integer, String, update as sqlalchemy_update
from sqlalchemy.future import select

from app.db.sqlalchemy import Base, async_db_session


class ModelAdminMixin:
    """Mixin for CRUD operations for models."""

    @classmethod
    async def create(cls, **kwargs: Any) -> None:
        """Create object."""
        async_db_session.add(cls(**kwargs))  # type: ignore
        await async_db_session.commit()

    @classmethod
    async def update(cls, id: int, **kwargs: Any) -> None:  # noqa: WPS125
        """Update object by id."""
        query = (
            sqlalchemy_update(cls)
            .where(cls.id == id)  # type: ignore
            .values(**kwargs)
            .execution_options(synchronize_session="fetch")
        )

        await async_db_session.execute(query)
        await async_db_session.commit()

    @classmethod
    async def get(cls, id: int) -> Any:  # noqa: WPS125
        """Get object by id."""
        query = select(cls).where(cls.id == id)  # type: ignore
        rows = await async_db_session.execute(query)
        (row,) = rows.one()
        return row  # noqa: WPS331

    @classmethod
    async def all(cls) -> Any:  # noqa: WPS125
        """Get all objects."""
        query = select(cls)
        rows = await async_db_session.execute(query)
        return rows.all()


class Record(Base, ModelAdminMixin):
    """Simple database model for example."""

    __tablename__ = "record"

    id: int = Column(Integer, primary_key=True, autoincrement=True)  # noqa: WPS125
    record_data: str = Column(String)

    def __repr__(self) -> str:
        """Show string representation of record."""
        return self.record_data
