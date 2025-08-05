import pytest
from deepdiff import DeepDiff
from sqlalchemy import func, select
from sqlalchemy.exc import DataError
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.repository.exceptions import (
    RecordDoesNotExistError,
    RecordAlreadyExistsError,
    ValidationError,
    RecordCreateError,
)
from app.domain.entities.sample_record import SampleRecord
from app.infrastructure.db.sample_record.models import SampleRecordModel
from app.infrastructure.repositories.sample_record import SampleRecordRepository
from tests.integration.factories import SampleRecordModelFactory


def assert_database_object_equal_domain(
    db_object: SampleRecordModel, domain_object: SampleRecord
) -> None:
    assert db_object.id == domain_object.id
    assert db_object.record_data == domain_object.record_data
    assert db_object.name == domain_object.name


async def test_add_record(
    sample_record_repository: SampleRecordRepository,
    isolated_session: AsyncSession,
):
    """Test adding a new record."""

    new_record = SampleRecord(record_data="test_add", name="test_name")
    created_record = await sample_record_repository.create(new_record)

    count = await isolated_session.scalar(
        select(func.count()).select_from(SampleRecordModel)
    )
    assert count == 1

    diff = DeepDiff(new_record, created_record, exclude_paths={"id"})
    assert not diff, diff

    db_object = await isolated_session.scalar(
        select(SampleRecordModel).where(SampleRecordModel.id == created_record.id)
    )
    assert_database_object_equal_domain(db_object, created_record)


async def test_add_record_with_non_unique_name(
    sample_record_factory: SampleRecordModelFactory,
    sample_record_repository: SampleRecordRepository,
    isolated_session: AsyncSession,
):
    existing_record = await sample_record_factory.create(
        record_data="test_add", name="test_name"
    )
    new_record = SampleRecord(record_data="new_data", name="test_name")

    with pytest.raises(RecordAlreadyExistsError):
        await sample_record_repository.create(new_record)


async def test_create_record_with_null_required_field(
    sample_record_repository: SampleRecordRepository,
):
    """Test creating a record with null required field raises ValidationError."""
    invalid_record = SampleRecord(record_data="test_add", name="test_name")  # type: ignore
    invalid_record.record_data = None

    with pytest.raises(ValidationError):
        await sample_record_repository.create(invalid_record)


async def test_repository_handles_unexpected_database_error(
    sample_record_repository: SampleRecordRepository,
    monkeypatch,
):
    """Test that unexpected database errors are re-raised as default exceptions."""

    async def mock_add_and_commit(*args, **kwargs):
        raise DataError("Unexpected database error", None, Exception())

    monkeypatch.setattr(
        sample_record_repository._session, "execute", mock_add_and_commit
    )

    record = SampleRecord(record_data="test_data", name="test_name")

    with pytest.raises(RecordCreateError):
        await sample_record_repository.create(record)


async def test_update_record(
    sample_record_repository: SampleRecordRepository,
    isolated_session: AsyncSession,
    sample_record_factory: type[SampleRecordModelFactory],
):
    """Test updating an existing record."""

    existing_record = await sample_record_factory()

    updated_record = SampleRecord(
        id=existing_record.id, record_data="updated_data", name="updated_name"
    )
    updated_record_from_repo = await sample_record_repository.update(updated_record)

    count = await isolated_session.scalar(
        select(func.count()).select_from(SampleRecordModel)
    )
    assert count == 1
    assert updated_record_from_repo.id == existing_record.id
    assert updated_record_from_repo.record_data == updated_record.record_data

    record_from_db = await isolated_session.scalar(
        select(SampleRecordModel).where(SampleRecordModel.id == existing_record.id)
    )

    assert_database_object_equal_domain(record_from_db, updated_record_from_repo)


async def test_update_record_with_non_unique_name(
    sample_record_factory: type[SampleRecordModelFactory],
    sample_record_repository: SampleRecordRepository,
    isolated_session: AsyncSession,
):
    existing_record_1 = await sample_record_factory.create()
    existing_record_2 = await sample_record_factory.create()

    updated_record_2 = SampleRecord(
        id=existing_record_2.id,
        record_data=existing_record_2.record_data,
        name=existing_record_1.name,
    )

    with pytest.raises(RecordAlreadyExistsError):
        await sample_record_repository.update(updated_record_2)


async def test_delete_record(
    sample_record_repository: SampleRecordRepository,
    isolated_session: AsyncSession,
    sample_record_factory: type[SampleRecordModelFactory],
):
    """Test deleting a record."""
    existing_record = await sample_record_factory.create()
    await sample_record_repository.delete(existing_record.id)

    db_records_count = await isolated_session.scalar(
        select(func.count()).select_from(SampleRecordModel)
    )
    assert db_records_count == 0


async def test_delete_non_exist_record(
    sample_record_repository: SampleRecordRepository,
):
    """Test deleting a not existing record raises the error."""

    with pytest.raises(RecordDoesNotExistError):
        await sample_record_repository.delete(42)


async def test_get_record(
    sample_record_repository: SampleRecordRepository, sample_record_factory
):
    existing_record = await sample_record_factory.create()
    record_from_db = await sample_record_repository.get_by_id(existing_record.id)

    assert_database_object_equal_domain(existing_record, record_from_db)


async def test_get_non_existing_record(
    sample_record_repository: SampleRecordRepository,
    isolated_session: AsyncSession,
):
    """Test get a not existing record raises the error."""

    with pytest.raises(RecordDoesNotExistError):
        await sample_record_repository.get_by_id(42)


async def test_get_all_records(
    sample_record_repository: SampleRecordRepository,
    sample_record_factory: type[SampleRecordModelFactory],
):
    existing_records_map = {
        record.id: record for record in await sample_record_factory.create_batch(4)
    }
    records = await sample_record_repository.get_all()

    assert len(existing_records_map) == len(records)

    for record in records:
        assert_database_object_equal_domain(existing_records_map[record.id], record)
