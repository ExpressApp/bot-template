import factory
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory  # type ignore
from factory import DictFactory, Factory

from app.domain.entities.sample_record import SampleRecord
from app.infrastructure.db.sample_record.models import SampleRecordModel
from app.presentation.bot.schemas.sample_record import (
    SampleRecordCreateRequestSchema,
    SampleRecordDeleteRequestSchema,
    SampleRecordUpdateRequestSchema,
)


class SampleRecordModelFactory(AsyncSQLAlchemyFactory):
    """Factory for sample record model objects in the database."""

    class Meta:
        model = SampleRecordModel

    record_data = factory.Faker("text")


class SampleRecordFactory(Factory):
    """Factory for sample record domain objects"""

    class Meta:
        model = SampleRecord

    record_data = factory.Faker("text")


class SampleRecordCreateSchemaFactory(Factory):
    """Factory for sample record create schema objects.

    Dict factory used to break dependency from inner schema object"""

    class Meta:
        model = SampleRecordCreateRequestSchema

    record_data = factory.Faker("text")


class SampleRecordUpdateSchemaFactory(DictFactory):
    """Factory for sample record update schema objects."""

    class Meta:
        model = SampleRecordUpdateRequestSchema

    id = factory.Faker("integer")
    record_data = factory.Faker("text")


class SampleRecordDeleteSchemaFactory(DictFactory):
    """Factory for sample record delete schema objects."""

    class Meta:
        model = SampleRecordDeleteRequestSchema

    id = factory.Faker("integer")
