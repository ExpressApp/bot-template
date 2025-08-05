import factory
from factory import DictFactory, Factory

from app.domain.entities.sample_record import SampleRecord
from app.presentation.bot.schemas.sample_record import (
    SampleRecordCreateRequestSchema,
    SampleRecordDeleteRequestSchema,
    SampleRecordUpdateRequestSchema,
)


class SampleRecordFactory(Factory):
    """Factory for sample record domain objects"""

    class Meta:
        model = SampleRecord

    record_data = factory.Faker("text", max_nb_chars=128)
    name = factory.Faker("text", max_nb_chars=32)


class SampleRecordCreateSchemaFactory(Factory):
    """Factory for sample record create schema objects."""

    class Meta:
        model = SampleRecordCreateRequestSchema

    record_data = factory.Faker("text", max_nb_chars=128)
    name = factory.Faker("text", max_nb_chars=32)


class SampleRecordUpdateSchemaFactory(Factory):
    """Factory for sample record update schema objects."""

    class Meta:
        model = SampleRecordUpdateRequestSchema

    id = factory.Faker("integer")
    record_data = factory.Faker("text", max_nb_chars=128)
    name = factory.Faker("text", max_nb_chars=32)


class SampleRecordDeleteSchemaFactory(Factory):
    """Factory for sample record delete schema objects."""

    class Meta:
        model = SampleRecordDeleteRequestSchema

    id = factory.Faker("integer")
