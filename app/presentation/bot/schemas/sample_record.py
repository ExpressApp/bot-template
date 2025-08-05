"""Domains."""

from typing import Self

from pydantic import BaseModel, Field


class SampleRecordResponseSchema(BaseModel):
    """Base schema for sample record presentation."""

    id: int
    record_data: str
    name: str

    class Config:
        orm_mode = True


class SampleRecordResponseListSchema(BaseModel):
    data: list[SampleRecordResponseSchema]

    class Config:
        orm_mode = True


class SampleRecordCreateRequestSchema(
    BaseModel,
):
    record_data: str = Field(..., min_length=1, max_length=128)
    name: str = Field(..., min_length=1, max_length=32)


class SampleRecordDeleteRequestSchema(BaseModel):
    id: int


class SampleRecordUpdateRequestSchema(BaseModel):
    id: int
    record_data: str | None = Field(..., min_length=1, max_length=128)
    name: str | None = Field(..., min_length=1, max_length=32)

    @classmethod
    def _from_plain_message_data(cls, message_data: str) -> Self:
        record_id, record_name, record_data = message_data.split(" ")
        return cls(id=record_id, record_name=record_name, record_data=record_data)  # type: ignore[arg-type]
