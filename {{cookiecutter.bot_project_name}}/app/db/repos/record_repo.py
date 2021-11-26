"""Record repo."""

from app.db.crud import CRUD
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
        await CRUD.create(
            self._session, model_cls=RecordModel, model_data={"record_data": text}
        )

    async def get_all(  # noqa: WPS218
        self,
    ) -> list[RecordModel]:
        """Get all objects."""
        return await CRUD.all(self._session, model_cls=RecordModel)

