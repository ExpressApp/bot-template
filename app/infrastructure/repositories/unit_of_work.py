import asyncio

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.repository.interfaces import (
    ISampleRecordRepository,
    ISampleRecordUnitOfWork,
)
from app.infrastructure.repositories.sample_record import SampleRecordRepository


class ReadOnlySampleRecordUnitOfWork(ISampleRecordUnitOfWork):
    def get_sample_record_repository(self) -> ISampleRecordRepository:
        if not self._session:
            raise RuntimeError("Session is not initialized")

        return SampleRecordRepository(self._session)

    def __init__(self, session_factory: async_sessionmaker):
        super().__init__()
        self.session_factory = session_factory
        self._session: AsyncSession | None = None

    async def __aenter__(self):
        self._session = self.session_factory()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            # Recommended for explicit resources cleanup
            await self._session.rollback()
        finally:
            await self._session.close()


class WriteSampleRecordUnitOfWork(ReadOnlySampleRecordUnitOfWork):
    """Unit of Work for write operations with full transaction management."""

    async def __aenter__(self):
        self._session = self.session_factory()
        await asyncio.wait_for(self._session.begin(), timeout=5)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type:
                await self._session.rollback()
            else:
                await self._session.commit()
        finally:
            await self._session.close()
