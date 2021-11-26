"""CRUD implementation."""

from typing import Any, TypeVar

from sqlalchemy import delete, insert, select, update as _update
from sqlalchemy.inspection import inspect

from app.db.sqlalchemy import AsyncSession

T = TypeVar("T")  # noqa: WPS111


class CRUD:
    @staticmethod
    async def create(
        session: AsyncSession, model_cls: Any, model_data: dict[str, Any]
    ) -> Any:
        """Create object."""
        query = insert(model_cls).values(**model_data)

        res = await session.execute(query)
        return res.inserted_primary_key

    @staticmethod
    async def update(
        session: AsyncSession, model_cls: Any, pkey_val: Any, model_data: dict[str, Any]
    ) -> None:
        """Update object by primary key."""
        primary_key = inspect(model_cls).primary_key[0]
        query = (
            _update(model_cls)
            .where(primary_key == pkey_val)
            .values(**model_data)
            .execution_options(synchronize_session="fetch")
        )

        await session.execute(query)

    @staticmethod
    async def delete(session: AsyncSession, model_cls: Any, pkey_val: Any) -> None:
        """Delete object by primary key value."""
        primary_key = inspect(model_cls).primary_key[0]
        query = delete(model_cls).where(primary_key == pkey_val)

        await session.execute(query)

    @staticmethod
    async def get(session: AsyncSession, model_cls: Any, pkey_val: Any) -> Any:
        """Get object by primary key."""
        primary_key = inspect(model_cls).primary_key[0]
        query = select(model_cls).where(primary_key == pkey_val)

        rows = await session.execute(query)
        return rows.scalars().one()

    @staticmethod
    async def get_or_none(session: AsyncSession, model_cls: Any, pkey_val: Any) -> Any:
        """Get object by primary key or none."""
        primary_key = inspect(model_cls).primary_key[0]
        query = select(model_cls).where(primary_key == pkey_val)

        rows = await session.execute(query)
        return rows.scalar()

    @staticmethod
    async def all(
        session: AsyncSession,
        model_cls: Any,
    ) -> Any:
        """Get all objects by db model."""
        query = select(model_cls)

        rows = await session.execute(query)
        return rows.scalars().all()

    @staticmethod
    async def get_by_field(
        session: AsyncSession, model_cls: Any, field: str, field_value: Any
    ) -> Any:
        """Return objects from db with condition field=val."""
        field = getattr(model_cls, field)

        query = select(model_cls).where(field == field_value)

        rows = await session.execute(query)
        return rows.scalars().all()
