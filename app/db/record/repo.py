"""Record repo."""

from typing import List, Optional

from app.db.crud import CRUD
from app.db.record.models import RecordModel
from app.db.sqlalchemy import AsyncSession
from app.schemas.record import Record


class RecordRepo:
    def __init__(self, session: AsyncSession):
        """Initialize repo with CRUD."""
        self._crud = CRUD(session=session, cls_model=RecordModel)

    async def create(self, record_data: str) -> Record:
        """Create record row in db."""
        row = await self._crud.create(model_data={"record_data": record_data})
        record_in_db = await self._crud.get(pkey_val=row.id)
        return Record.from_orm(record_in_db)

    async def update(self, record_id: int, record_data: str) -> Record:
        """Update record row in db."""
        await self._crud.update(
            pkey_val=record_id,
            model_data={"record_data": record_data},
        )
        record_in_db = await self._crud.get(pkey_val=record_id)
        return Record.from_orm(record_in_db)

    async def delete(self, record_id: int) -> None:
        await self._crud.delete(pkey_val=record_id)

    async def get(self, record_id: int) -> Record:
        record = await self._crud.get(pkey_val=record_id)
        return Record.from_orm(record)

    async def get_or_none(self, record_id: int) -> Optional[Record]:
        record = await self._crud.get_or_none(pkey_val=record_id)
        if record:
            return Record.from_orm(record)

        return None

    async def get_all(self) -> List[Record]:
        """Get all objects."""
        records_in_db = await self._crud.all()
        return [Record.from_orm(record) for record in records_in_db]

    async def filter_by_record_data(self, record_data: str) -> List[Record]:
        """Get all objects."""
        records_in_db = await self._crud.get_by_field(
            field="record_data",
            field_value=record_data,
        )
        return [Record.from_orm(record) for record in records_in_db]
