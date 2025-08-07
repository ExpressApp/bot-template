"""Domains."""

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

    class Config:
        orm_mode = True


class SampleRecordUpdateRequestSchema(
    BaseModel,
):
    id: int
    record_data: str = Field(..., min_length=1, max_length=128)
    name: str = Field(..., min_length=1, max_length=32)

    class Config:
        orm_mode = True


class SampleRecordGetOrDeleteRequestSchema(BaseModel):
    """Schema for sample record get or delete request."""

    id: int
