"""Domains."""

from pydantic import BaseModel, Field, ConfigDict


class SampleRecordResponseSchema(BaseModel):
    """Base schema for sample record presentation."""

    id: int
    record_data: str
    name: str

    model_config = ConfigDict(from_attributes=True)


class SampleRecordResponseListSchema(BaseModel):
    data: list[SampleRecordResponseSchema]

    model_config = ConfigDict(from_attributes=True)


class SampleRecordCreateRequestSchema(
    BaseModel,
):
    record_data: str = Field(..., min_length=1, max_length=128)
    name: str = Field(..., min_length=1, max_length=32)

    model_config = ConfigDict(from_attributes=True)


class SampleRecordUpdateRequestSchema(
    BaseModel,
):
    id: int
    record_data: str = Field(..., min_length=1, max_length=128)
    name: str = Field(..., min_length=1, max_length=32)

    model_config = ConfigDict(from_attributes=True)


class SampleRecordGetOrDeleteRequestSchema(BaseModel):
    """Schema for sample record get or delete request."""

    id: int
