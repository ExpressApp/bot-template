from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.repository.interfaces import (
    ISampleRecordRepository,
    ISampleRecordUnitOfWork,
)
from app.infrastructure.repositories.sample_record import SampleRecordRepository


class ReadOnlySampleRecordUnitOfWork(ISampleRecordUnitOfWork):
    def __init__(self, session_factory: async_sessionmaker):
        super().__init__()
        self.session_factory = session_factory
        self._session: AsyncSession | None = None

    def get_sample_record_repository(self) -> ISampleRecordRepository:
        if not self._session:
            raise RuntimeError("Session is not initialized")

        return SampleRecordRepository(self._session)

    async def __aenter__(self) -> Self:
        self._session = self.session_factory()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if not self._session:
            return

        try:
            if exc_type is not None or self._session.in_transaction():
                await self._session.rollback()
        finally:
            await self._session.close()
            self._session = None


class WriteSampleRecordUnitOfWork(ReadOnlySampleRecordUnitOfWork):
    """Unit of Work for write operations with full transaction management."""

    async def __aenter__(self) -> Self:
        self._session = self.session_factory()

        await self._session.begin()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if not self._session:
            return

        try:
            if exc_type:
                await self._session.rollback()
            else:
                await self._session.commit()
        finally:
            await self._session.close()
