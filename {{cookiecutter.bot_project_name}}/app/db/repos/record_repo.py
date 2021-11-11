"""Record repo."""

from sqlalchemy import insert, select

from app.db.models import Record
from app.db.sqlalchemy import AsyncSession


class RecordRepo:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_record(
        self,
        text: str,
    ) -> None:
        """Create record row in db."""
        query = insert(Record).values(record_data=text)
        await self._session.execute(query)

    async def get_all(  # noqa: WPS218
        self,
    ) -> list[Record]:
        """Get all objects."""
        query = select(Record)

        rows = await self._session.execute(query)
        return rows.scalars().all()
