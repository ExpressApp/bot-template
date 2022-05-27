"""Domains."""

from pydantic import BaseModel

from app.db.record.models import RecordModel


class Record(BaseModel):
    id: int
    record_data: str

    @classmethod
    def from_orm(cls, record: RecordModel) -> "Record":
        return cls(id=record.id, record_data=record.record_data)
