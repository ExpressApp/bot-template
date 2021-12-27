"""CRUD implementation."""

from typing import Any, TypeVar

from sqlalchemy import delete, insert, select, update
from sqlalchemy.inspection import inspect

from app.db.sqlalchemy import AsyncSession

T = TypeVar("T")  # noqa: WPS111


class CRUD:
    """CRUD operations for models."""

    def __init__(self, session: AsyncSession, cls_model: Any):
        self._session = session
        self._cls_model = cls_model

    async def create(self, *, model_data: dict[str, Any]) -> Any:
        """Create object."""
        query = insert(self._cls_model).values(**model_data)

        res = await self._session.execute(query)
        return res.inserted_primary_key

    async def update(
        self,
        *,
        pkey_val: Any,
        model_data: dict[str, Any],
    ) -> None:
        """Update object by primary key."""
        primary_key = inspect(self._cls_model).primary_key[0]
        query = (
            update(self._cls_model)
            .where(primary_key == pkey_val)
            .values(**model_data)
            .execution_options(synchronize_session="fetch")
        )

        await self._session.execute(query)

    async def delete(self, *, pkey_val: Any) -> None:
        """Delete object by primary key value."""
        primary_key = inspect(self._cls_model).primary_key[0].name
        query = (
            delete(self._cls_model)
            .where(getattr(self._cls_model, primary_key) == pkey_val)
            .execution_options(synchronize_session="fetch")
        )

        await self._session.execute(query)

    async def get(self, *, pkey_val: Any) -> Any:
        """Get object by primary key."""
        primary_key = inspect(self._cls_model).primary_key[0]
        query = select(self._cls_model).where(primary_key == pkey_val)

        rows = await self._session.execute(query)
        return rows.scalars().one()

    async def get_or_none(self, *, pkey_val: Any) -> Any:
        """Get object by primary key or none."""
        primary_key = inspect(self._cls_model).primary_key[0]
        query = select(self._cls_model).where(primary_key == pkey_val)

        rows = await self._session.execute(query)
        return rows.scalar()

    async def all(
        self,
    ) -> Any:
        """Get all objects by db model."""
        query = select(self._cls_model)

        rows = await self._session.execute(query)
        return rows.scalars().all()

    async def get_by_field(self, *, field: str, field_value: Any) -> Any:
        """Return objects from db with condition field=val."""
        query = select(self._cls_model).where(
            getattr(self._cls_model, field) == field_value
        )

        rows = await self._session.execute(query)
        return rows.scalars().all()
