import factory
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory

from app.infrastructure.db.sample_record.models import SampleRecordModel


class SampleRecordModelFactory(AsyncSQLAlchemyFactory):
    """Factory for sample record model objects in the database."""

    class Meta:
        model = SampleRecordModel

    record_data = factory.Faker("text")
