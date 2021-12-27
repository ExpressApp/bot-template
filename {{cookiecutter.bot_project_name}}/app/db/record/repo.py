"""Record repo."""


from app.db.crud import CRUD
from app.db.record.models import RecordModel
from app.db.sqlalchemy import AsyncSession
from app.schemas.record import Record


class RecordRepo:
    def __init__(self, session: AsyncSession):
        """Initialize repo with CRUD."""
        self._crud = CRUD(session=session, cls_model=RecordModel)

    async def create_record(
        self,
        text: str,
    ) -> Record:
        """Create record row in db."""
        row = await self._crud.create(model_data={"record_data": text})
        record_in_db = await self._crud.get(pkey_val=row.id)
        return Record.from_orm(record_in_db)

    async def get_all(
        self,
    ) -> list[Record]:
        """Get all objects."""
        records_in_db = await self._crud.all()
        return [Record.from_orm(record) for record in records_in_db]
