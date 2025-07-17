from typing import List

from app.application.repository.exceptions import RecordDoesNotExistError
from app.application.repository.interfaces import ISampleRecordRepository
from app.domain.entities.sample_record import SampleRecord


class FakeSampleRecordRepository(ISampleRecordRepository):
    def __init__(self, records: List[SampleRecord] = None):
        self._records = {}
        if records:
            for id, record in enumerate(records):
                record.id = id
                self._records[record.id] = record

    async def create(self, record: SampleRecord) -> SampleRecord:
        if record.id is None:
            record.id = len(self._records) + 1

        self._records[record.id] = record
        return record

    async def update(self, record: SampleRecord) -> SampleRecord:
        if record.id not in self._records:
            raise RecordDoesNotExistError(f"Record with id={record.id} does not exist.")

        self._records[record.id] = record
        return record

    async def delete(self, record_id: int) -> int:
        if record_id not in self._records:
            raise RecordDoesNotExistError(f"Record with id={record_id} does not exist.")

        del self._records[record_id]
        return record_id

    async def get_by_id(self, record_id: int) -> SampleRecord:
        if record_id not in self._records:
            raise RecordDoesNotExistError(f"Record with id={record_id} does not exist.")

        return self._records[record_id]

    async def get_all(self) -> List[SampleRecord]:
        return list(self._records.values())
