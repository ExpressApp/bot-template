import pytest

from app.application.repository.exceptions import RecordDoesNotExistError
from app.application.use_cases.interfaces import ISampleRecordUseCases
from app.presentation.bot.schemas.sample_record import (
    SampleRecordResponseListSchema,
    SampleRecordResponseSchema,
)
from tests.factories import (
    SampleRecordCreateSchemaFactory,
    SampleRecordUpdateSchemaFactory,
)


async def test_sample_record_use_case_add_record(
    sample_record_use_cases_with_fake_repo: ISampleRecordUseCases,
):
    sample_record_create_request = SampleRecordCreateSchemaFactory()
    response = await sample_record_use_cases_with_fake_repo.create_record(
        sample_record_create_request  # type: ignore
    )

    assert isinstance(response, SampleRecordResponseSchema)
    assert response.record_data == sample_record_create_request.record_data


async def test_sample_record_use_case_update_record(
    sample_record_use_cases_with_fake_repo: ISampleRecordUseCases,
):
    existing_record = await sample_record_use_cases_with_fake_repo.create_record(
        SampleRecordCreateSchemaFactory()  # type: ignore
    )

    update_request = SampleRecordUpdateSchemaFactory(id=existing_record.id)

    response = await sample_record_use_cases_with_fake_repo.update_record(
        update_request  # type: ignore
    )

    assert isinstance(response, SampleRecordResponseSchema)
    assert response.record_data == update_request.record_data


async def test_sample_record_use_case_delete_record(
    sample_record_use_cases_with_fake_repo: ISampleRecordUseCases,
):
    existing_record = await sample_record_use_cases_with_fake_repo.create_record(
        SampleRecordCreateSchemaFactory()  # type: ignore
    )

    record = await sample_record_use_cases_with_fake_repo.get_record(existing_record.id)

    assert record == existing_record

    await sample_record_use_cases_with_fake_repo.delete_record(existing_record.id)

    with pytest.raises(RecordDoesNotExistError):
        await sample_record_use_cases_with_fake_repo.get_record(existing_record.id)


async def test_sample_record_use_case_get_record(
    sample_record_use_cases_with_fake_repo: ISampleRecordUseCases,
):
    existing_record = await sample_record_use_cases_with_fake_repo.create_record(
        SampleRecordCreateSchemaFactory()  # type: ignore
    )

    response = await sample_record_use_cases_with_fake_repo.get_record(
        existing_record.id
    )
    assert isinstance(response, SampleRecordResponseSchema)
    assert response.record_data == existing_record.record_data
    assert response.id == existing_record.id


async def test_sample_record_use_case_get_all_records(
    sample_record_use_cases_with_fake_repo: ISampleRecordUseCases,
):
    existing_records = [
        await sample_record_use_cases_with_fake_repo.create_record(request)
        for request in SampleRecordCreateSchemaFactory.create_batch(3)
    ]

    response = await sample_record_use_cases_with_fake_repo.get_all_records()

    assert isinstance(response, SampleRecordResponseListSchema)
    assert len(response.data) == len(existing_records)

    for record, response_record in zip(existing_records, response.data, strict=True):
        assert record.id == response_record.id
        assert record.record_data == response_record.record_data


async def test_delete_non_existing_record_raises_error(
    sample_record_use_cases_with_fake_repo: ISampleRecordUseCases,
):
    """Test deleting a not existing record re raises the error from repository."""

    with pytest.raises(RecordDoesNotExistError):
        await sample_record_use_cases_with_fake_repo.delete_record(42)


async def test_update_non_existing_record_raises_error(
    sample_record_use_cases_with_fake_repo: ISampleRecordUseCases,
):
    """Test deleting a not existing record re raises the error from repository."""

    with pytest.raises(RecordDoesNotExistError):
        await sample_record_use_cases_with_fake_repo.update_record(
            SampleRecordUpdateSchemaFactory(id=42)  # type: ignore
        )


async def test_get_non_existing_record_raises_error(
    sample_record_use_cases_with_fake_repo: ISampleRecordUseCases,
):
    """Test deleting a not existing record re raises the error from repository."""

    with pytest.raises(RecordDoesNotExistError):
        await sample_record_use_cases_with_fake_repo.get_record(42)
