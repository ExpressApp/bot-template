"""Interfaces for application use cases."""

from abc import ABC, abstractmethod

from app.presentation.bot.schemas.sample_record import (
    SampleRecordCreateRequestSchema,
    SampleRecordResponseSchema,
    SampleRecordUpdateRequestSchema,
    SampleRecordResponseListSchema,
)


class ISampleRecordUseCases(ABC):
    """Interface for record use cases."""

    @abstractmethod
    async def create_record(
        self, create_request: SampleRecordCreateRequestSchema
    ) -> SampleRecordResponseSchema:
        """Create a new record."""
        pass

    @abstractmethod
    async def update_record(
        self, update_request: SampleRecordUpdateRequestSchema
    ) -> SampleRecordResponseSchema:
        """Update an existing record."""
        pass

    @abstractmethod
    async def delete_record(self, record_id: int) -> None:
        """Delete a record."""
        pass

    @abstractmethod
    async def get_record(self, record_id: int) -> SampleRecordResponseSchema:
        """Get a record by ID."""
        pass

    @abstractmethod
    async def get_all_records(self) -> SampleRecordResponseListSchema:
        """Get all records."""
        pass
