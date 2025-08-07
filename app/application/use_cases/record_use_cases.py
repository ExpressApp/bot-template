"""Implementation of record use cases."""

from app.application.repository.interfaces import ISampleRecordRepository
from app.application.use_cases.interfaces import ISampleRecordUseCases
from app.domain.entities.sample_record import SampleRecord
from app.presentation.bot.schemas.sample_record import (
    SampleRecordCreateRequestSchema,
    SampleRecordResponseListSchema,
    SampleRecordResponseSchema,
    SampleRecordUpdateRequestSchema,
)


class SampleRecordUseCases(ISampleRecordUseCases):
    """Implementation of record use cases."""

    def __init__(self, record_repo: ISampleRecordRepository):
        self._repo = record_repo

    async def create_record(
        self, request_object: SampleRecordCreateRequestSchema
    ) -> SampleRecordResponseSchema:
        domain_object = SampleRecord(
            record_data=request_object.record_data, name=request_object.name
        )
        created_record = SampleRecordResponseSchema.from_orm(
            await self._repo.create(domain_object)
        )

        return created_record

    async def update_record(
        self, update_request: SampleRecordUpdateRequestSchema
    ) -> SampleRecordResponseSchema:
        """Update an existing record."""
        domain_object = SampleRecord(
            record_data=update_request.record_data,
            id=update_request.id,
            name=update_request.name,
        )
        updated_record = SampleRecordResponseSchema.from_orm(
            await self._repo.update(domain_object)
        )
        return updated_record

    async def delete_record(self, record_id: int) -> None:
        """Delete a record."""
        await self._repo.delete(record_id)

    async def get_record(self, record_id: int) -> SampleRecordResponseSchema:
        """Get a record by ID."""
        fetched_record = await self._repo.get_by_id(record_id)
        return SampleRecordResponseSchema.from_orm(fetched_record)

    async def get_all_records(self) -> SampleRecordResponseListSchema:
        """Get all records."""
        fetched_records = await self._repo.get_all()
        response_records = [
            SampleRecordResponseSchema.from_orm(record) for record in fetched_records
        ]
        return SampleRecordResponseListSchema(data=response_records)
