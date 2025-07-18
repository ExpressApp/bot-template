"""Domains."""

from typing import Self

from pydantic import BaseModel, Field


class SampleRecordResponseSchema(BaseModel):
    """Base schema for sample record presentation."""

    id: int
    record_data: str

    class Config:
        orm_mode = True


class SampleRecordResponseListSchema(BaseModel):
    data: list[SampleRecordResponseSchema]

    class Config:
        orm_mode = True


class SampleRecordCreateRequestSchema(
    BaseModel,
):
    record_data: str = Field(..., min_length=1)


class SampleRecordDeleteRequestSchema(BaseModel):
    id: int


class SampleRecordUpdateRequestSchema(BaseModel):
    id: int
    record_data: str = Field(..., min_length=1)

    @classmethod
    def _from_plain_message_data(cls, message_data: str) -> Self:
        record_id, record_data = message_data.split(" ")
        return cls(id=record_id, record_data=record_data)  # type: ignore[arg-type]
