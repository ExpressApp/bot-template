"""Record repository interface."""

from abc import ABC, abstractmethod
from typing import List

from app.domain.entities.sample_record import SampleRecord


class ISampleRecordRepository(ABC):
    """Interface for record repository operations."""

    @abstractmethod
    async def create(self, record: SampleRecord) -> SampleRecord:
        """
        Create a new record in database
        Parameters:
            record: The record to be created.

        Returns:
            SampleRecord: The newly created record of type SampleRecord.
        """
        pass

    @abstractmethod
    async def update(self, record: SampleRecord) -> SampleRecord:
        """
        Update an existing record in database
        Parameters:
            record: The record to be created.

        Returns:
            SampleRecord: The newly created record of type SampleRecord.
        """
        pass

    @abstractmethod
    async def delete(self, record_id: int) -> None:
        """
        Delete a record from the database by provided id

        Parameters:
            record_id: The unique identifier of the record to be deleted.

        Returns:
            An id of the deleted record
        """
        pass

    @abstractmethod
    async def get_by_id(self, record_id: int) -> SampleRecord:
        """Get the record from the database by provided id
        Parameters:
            record_id: The record id to be created.

        Returns:
            SampleRecord: The record from a database."""
        pass

    @abstractmethod
    async def get_all(self) -> List[SampleRecord]:
        """Get all records from the database"""
        pass
