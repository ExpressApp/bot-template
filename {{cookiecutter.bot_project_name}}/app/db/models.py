"""Database models declarations."""

from typing import Any, Generic, List, TypeVar

from sqlalchemy import Column, Integer, String, insert, update as _update
from sqlalchemy.future import select
from sqlalchemy.inspection import inspect

from app.db.sqlalchemy import Base, session

T = TypeVar("T")  # noqa: WPS111


class CRUDMixin(Generic[T]):
    """Mixin for CRUD operations for models."""

    @classmethod
    async def create(cls, **kwargs: Any) -> None:
        """Create object."""
        query = insert(cls).values(**kwargs)
        async with session.begin():
            await session.execute(query)

    @classmethod
    async def update(cls, pkey_val: int, **kwargs: Any) -> None:  # noqa: WPS125
        """Update object by id."""
        primary_key = inspect(cls).primary_key[0]
        query = (
            _update(cls)
            .where(primary_key == pkey_val)
            .values(**kwargs)
            .execution_options(synchronize_session="fetch")
        )
        async with session.begin():
            await session.execute(query)

    @classmethod
    async def get(cls, pkey_val: int) -> T:  # noqa: WPS125
        """Get object by id."""
        primary_key = inspect(cls).primary_key[0]
        query = select(cls).where(primary_key == pkey_val)
        async with session.begin():
            rows = await session.execute(query)
        return rows.scalars().one()

    @classmethod
    async def all(cls) -> List[T]:  # noqa: WPS125
        """Get all objects."""
        query = select(cls)
        async with session.begin():
            rows = await session.execute(query)
        return rows.scalars().all()


class Record(Base, CRUDMixin):
    """Simple database model for example."""

    __tablename__ = "record"

    id: int = Column(Integer, primary_key=True, autoincrement=True)  # noqa: WPS125
    record_data: str = Column(String)

    def __repr__(self) -> str:
        """Show string representation of record."""
        return self.record_data
