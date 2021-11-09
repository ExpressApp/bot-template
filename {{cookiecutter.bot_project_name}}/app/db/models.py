"""Database models declarations."""

from typing import Any, Generic, List, TypeVar

from sqlalchemy import Column, Integer, String, delete, insert, update as _update
from sqlalchemy.future import select
from sqlalchemy.inspection import inspect

from app.db.sqlalchemy import Base, async_db_connection

T = TypeVar("T")  # noqa: WPS111


class CRUDMixin(Generic[T]):
    """Mixin for CRUD operations for models."""

    @classmethod
    async def create(cls, **kwargs: Any) -> None:
        """Create object."""
        query = insert(cls).values(**kwargs)
        session = await async_db_connection.get_session()
        async with session.begin():
            await session.execute(query)
            await session.flush()

    @classmethod
    async def update(cls, pkey_val: Any, **kwargs: Any) -> None:  # noqa: WPS125
        """Update object by id."""
        primary_key = inspect(cls).primary_key[0]
        query = (
            _update(cls)
            .where(primary_key == pkey_val)
            .values(**kwargs)
            .execution_options(synchronize_session="fetch")
        )

        session = await async_db_connection.get_session()
        async with session.begin():
            await session.execute(query)
            await session.flush()

    @classmethod
    async def get(cls, pkey_val: Any) -> T:  # noqa: WPS125
        """Get object by id."""
        primary_key = inspect(cls).primary_key[0]
        query = select(cls).where(primary_key == pkey_val)

        session = await async_db_connection.get_session()
        async with session.begin():
            rows = await session.execute(query)
        return rows.scalars().one()

    @classmethod
    async def all(cls) -> List[T]:  # noqa: WPS125
        """Get all objects."""
        query = select(cls)
        session = await async_db_connection.get_session()
        async with session.begin():
            rows = await session.execute(query)
        return rows.scalars().all()

    @classmethod
    async def delete(cls, pkey_val: Any) -> Any:
        """Delete object by primary key value."""
        primary_key = inspect(cls).primary_key[0]
        query = delete(cls).where(primary_key == pkey_val)

        session = await async_db_connection.get_session()
        async with session.begin():
            await session.execute(query)
            await session.flush()


class Record(Base, CRUDMixin):
    """Simple database model for example."""

    __tablename__ = "record"

    id: int = Column(Integer, primary_key=True, autoincrement=True)  # noqa: WPS125
    record_data: str = Column(String)

    def __repr__(self) -> str:
        """Show string representation of record."""
        return self.record_data
