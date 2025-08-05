from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.interfaces import ISampleRecordUseCases
from app.infrastructure.db.sample_record.models import SampleRecordModel
from app.presentation.bot.schemas.sample_record import SampleRecordResponseSchema
from tests.factories import SampleRecordCreateSchemaFactory
from tests.integration.factories import SampleRecordModelFactory


def assert_database_object_equal_to_retrieved_object(
    database_object: SampleRecordModel, retrieved_object: SampleRecordResponseSchema
):
    assert isinstance(retrieved_object, SampleRecordResponseSchema)
    assert database_object.id == retrieved_object.id
    assert database_object.record_data == retrieved_object.record_data
    assert database_object.name == retrieved_object.name


async def test_sample_record_use_case_add_record_in_database(
    sample_record_use_cases_with_real_repo: ISampleRecordUseCases,
    isolated_session: AsyncSession,
):
    """Test adding a new record."""

    sample_record_create_request = SampleRecordCreateSchemaFactory()
    response = await sample_record_use_cases_with_real_repo.create_record(
        sample_record_create_request  # type: ignore
    )

    query = select(SampleRecordModel).where(SampleRecordModel.id == response.id)
    result = (await isolated_session.execute(query)).scalar_one()

    assert_database_object_equal_to_retrieved_object(result, response)


async def test_sample_record_use_case_get_record_from_database(
    sample_record_use_cases_with_real_repo: ISampleRecordUseCases,
    isolated_session: AsyncSession,
    sample_record_factory:type[SampleRecordModelFactory]
):
    """Test get a record."""



    existing_record = await sample_record_factory.create()

    response = await sample_record_use_cases_with_real_repo.get_record(
        existing_record.id
    )

    assert isinstance(response, SampleRecordResponseSchema)
    assert response.record_data == existing_record.record_data
    assert response.id == existing_record.id


async def test_sample_record_use_case_remove_record_from_database(
    sample_record_use_cases_with_real_repo: ISampleRecordUseCases,
    isolated_session: AsyncSession,
    sample_record_factory:type[SampleRecordModelFactory]
):
    """Test adding a new record."""

    existing_record = await sample_record_factory.create()

    await sample_record_use_cases_with_real_repo.delete_record(existing_record.id)

    assert await isolated_session.get(SampleRecordModel, existing_record.id) is None


async def test_sample_record_use_case_get_all_records_from_database(
    sample_record_use_cases_with_real_repo: ISampleRecordUseCases,
    isolated_session: AsyncSession,
    sample_record_factory: SampleRecordModelFactory,
):
    """Test get all records from database"""
    existing_records = {
        record.id: record for record in await sample_record_factory.create_batch(3)
    }

    response = await sample_record_use_cases_with_real_repo.get_all_records()

    for response_record in response.data:
        assert_database_object_equal_to_retrieved_object(
            existing_records[response_record.id], response_record
        )
