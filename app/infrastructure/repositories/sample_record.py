"""Record repository implementation."""

from typing import List

from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import NoResultFound, SQLAlchemyError

from app.application.repository.exceptions import (
    RecordCreateError,
    RecordDeleteError,
    RecordDoesNotExistError,
    RecordRetreiveError,
    RecordUpdateError,
)
from app.application.repository.interfaces import ISampleRecordRepository
from app.decorators.exceptions_mapper import exception_mapper
from app.domain.entities.sample_record import SampleRecord
from app.infrastructure.db.sample_record.models import SampleRecordModel
from app.infrastructure.db.sqlalchemy import AsyncSession


class SampleRecordRepository(ISampleRecordRepository):
    """Implementation of the record repository interface."""

    def __init__(self, session: AsyncSession):
        """Initialize the repository with a database session.

        Args:
            session: The database session.
        """
        self._session = session

    @exception_mapper(
        catch_exceptions=SQLAlchemyError, raise_exception=RecordCreateError
    )
    async def create(self, record: SampleRecord) -> SampleRecord:
        query = (
            insert(SampleRecordModel)
            .values(record_data=record.record_data)
            .returning(SampleRecordModel)
        )
        result = await self._session.execute(query)
        await self._session.flush()
        record_model = result.scalar_one()
        return self._to_domain_object(record_model)

    @exception_mapper(
        catch_exceptions=SQLAlchemyError, raise_exception=RecordUpdateError
    )
    async def update(self, record: SampleRecord) -> SampleRecord:
        query = (
            update(SampleRecordModel)
            .where(SampleRecordModel.id == record.id)
            .values(record_data=record.record_data)
            .returning(SampleRecordModel)
        )
        execute_result = (await self._session.execute(query)).scalar_one_or_none()
        await self._session.flush()
        if execute_result is None:
            raise RecordDoesNotExistError(
                f"Sample record with id={record.id} does not exist."
            )

        return self._to_domain_object(execute_result)

    @exception_mapper(
        catch_exceptions=SQLAlchemyError, raise_exception=RecordDeleteError
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

    @exception_mapper(
        catch_exceptions=NoResultFound, raise_exception=RecordDoesNotExistError
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

    @exception_mapper(
        catch_exceptions=SQLAlchemyError, raise_exception=RecordRetreiveError
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
        )
