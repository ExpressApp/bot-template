"""Record repository interface."""

from abc import ABC, abstractmethod
from typing import List, Optional

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
    async def delete(self, record_id: int) -> int:
        """
        Delete a record from the database by provided id

        Parameters:
            record_id: The unique identifier of the record to be deleted.

        Returns:
            None

        This method does not return any value.

        Raises:
            NotImplementedError: If this method is not overridden in the implementing class.
        """
        pass

    @abstractmethod
    async def get_by_id(self, record_id: int) -> SampleRecord:
        """Get the record from the database by provided id
        Parameters:
            record_id: The record id to be created.

        Returns:
            SampleRecord: The record from database."""
        pass

    @abstractmethod
    async def get_all(self) -> List[SampleRecord]:
        """Get all records from the database"""
        pass
