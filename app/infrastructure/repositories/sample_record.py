"""Record repository implementation."""

from typing import List

from psycopg2 import errorcodes
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError, NoResultFound, SQLAlchemyError

from app.application.repository.exceptions import (
    ForeignKeyError,
    RecordAlreadyExistsError,
    RecordCreateError,
    RecordDeleteError,
    RecordDoesNotExistError,
    RecordRetrieveError,
    RecordUpdateError,
    ValidationError,
)
from app.application.repository.interfaces import ISampleRecordRepository
from app.decorators.mapper.context import ExceptionContext
from app.decorators.mapper.exception_mapper import (
    ExceptionMapper,
)
from app.decorators.mapper.factories import EnrichedExceptionFactory
from app.domain.entities.sample_record import SampleRecord
from app.infrastructure.db.sample_record.models import SampleRecordModel
from app.infrastructure.db.sqlalchemy import AsyncSession


class IntegrityErrorFactory(EnrichedExceptionFactory):
    def make_exception(self, context: ExceptionContext) -> Exception:
        if not (orig := getattr(context.original_exception, "orig", None)):
            return self.generated_error(context.formatted_context)

        if not (sqlstate := getattr(orig, "sqlstate", None)):
            return self.generated_error(context.formatted_context)

        if sqlstate == errorcodes.UNIQUE_VIOLATION:
            return RecordAlreadyExistsError(context.formatted_context)

        if sqlstate == errorcodes.FOREIGN_KEY_VIOLATION:
            return ForeignKeyError(context.formatted_context)

        if sqlstate == errorcodes.NOT_NULL_VIOLATION:
            return ValidationError(context.formatted_context)

        return self.generated_error(context.formatted_context)


class SampleRecordRepository(ISampleRecordRepository):
    """Implementation of the record repository interface."""

    def __init__(self, session: AsyncSession):
        """Initialize the repository with a database session.

        Args:
            session: The database session.
        """
        self._session = session

    @ExceptionMapper(
        {
            IntegrityError: IntegrityErrorFactory(RecordCreateError),
            Exception: EnrichedExceptionFactory(RecordCreateError),
        },
        is_bound_method=True,
    )
    async def create(self, record: SampleRecord) -> SampleRecord:
        query = (
            insert(SampleRecordModel)
            .values(record_data=record.record_data, name=record.name)
            .returning(SampleRecordModel)
        )
        result = await self._session.execute(query)
        await self._session.flush()
        record_model = result.scalar_one()
        return self._to_domain_object(record_model)

    @ExceptionMapper(
        {
            IntegrityError: IntegrityErrorFactory(RecordUpdateError),
            Exception: EnrichedExceptionFactory(RecordUpdateError),
        },
        is_bound_method=True,
    )
    async def update(self, record: SampleRecord) -> SampleRecord:
        query = (
            update(SampleRecordModel)
            .where(SampleRecordModel.id == record.id)
            .values(record_data=record.record_data, name=record.name)
            .returning(SampleRecordModel)
        )
        execute_result = (await self._session.execute(query)).scalar_one_or_none()
        await self._session.flush()
        if execute_result is None:
            raise RecordDoesNotExistError(
                f"Sample record with id={record.id} does not exist."
            )

        return self._to_domain_object(execute_result)

    @ExceptionMapper(
        {
            SQLAlchemyError: EnrichedExceptionFactory(RecordDeleteError),
        },
        is_bound_method=True,
    )
    async def delete(self, record_id: int) -> None:
        """Delete a record.

        Args:
            record_id: The ID of the record to delete.
        """
        query = (
            delete(SampleRecordModel)
            .where(SampleRecordModel.id == record_id)
            .execution_options(synchronize_session="fetch")
            .returning(SampleRecordModel.id)
        )

        deletion_result = (await self._session.execute(query)).scalar_one_or_none()

        if deletion_result is None:
            raise RecordDoesNotExistError(
                f"Sample record with id={record_id} does not exist."
            )

        await self._session.flush()

    @ExceptionMapper(
        {
            NoResultFound: EnrichedExceptionFactory(RecordDoesNotExistError),
            Exception: EnrichedExceptionFactory(RecordRetrieveError),
        },
        is_bound_method=True,
    )
    async def get_by_id(self, record_id: int) -> SampleRecord:
        """Get a record by ID.

        Args:
            record_id: The ID of the record to get.

        Returns:
            The record as a domain entity.

        Raises:
            RecordNotFoundError: If the record is not found.
        """
        query = select(SampleRecordModel).where(SampleRecordModel.id == record_id)
        result = await self._session.execute(query)
        return self._to_domain_object(result.scalar_one())

    @ExceptionMapper(
        {
            Exception: EnrichedExceptionFactory(RecordRetrieveError),
        },
        is_bound_method=True,
    )
    async def get_all(self) -> List[SampleRecord]:
        """Get all records.

        Returns:
            A list of all records as domain entities.
        """
        query = select(SampleRecordModel)
        result = await self._session.execute(query)
        record_models = result.scalars().all()

        return [self._to_domain_object(record) for record in record_models]

    def _to_domain_object(self, record_model: SampleRecordModel) -> SampleRecord:
        """Convert a database model to a domain entity.

        Args:
            record_model: The database model to convert.

        Returns:
            The corresponding domain entity.
        """
        return SampleRecord(
            id=record_model.id,
            record_data=record_model.record_data,
            name=record_model.name,
        )
