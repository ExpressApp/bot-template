"""Record repo."""

from sqlalchemy import insert, select

from app.db.models import RecordModel
from app.db.sqlalchemy import AsyncSession


class RecordRepo:
    def __init__(self, session: AsyncSession):
        """Initialize repo with session."""
        self._session = session

    async def create_record(
        self,
        text: str,
    ) -> None:
        """Create record row in db."""
        query = insert(RecordModel).values(record_data=text)
        await self._session.execute(query)

    async def get_all(  # noqa: WPS218
        self,
    ) -> list[RecordModel]:
        """Get all objects."""
        query = select(RecordModel)

        rows = await self._session.execute(query)
        return rows.scalars().all()
