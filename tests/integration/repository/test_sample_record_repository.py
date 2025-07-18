import pytest
from deepdiff import DeepDiff
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.repository.exceptions import RecordDoesNotExistError
from app.domain.entities.sample_record import SampleRecord
from app.infrastructure.db.sample_record.models import SampleRecordModel
from app.infrastructure.repositories.sample_record import SampleRecordRepository
from tests.factories import SampleRecordModelFactory


def assert_database_object_equal_domain(
    db_object: SampleRecordModel, domain_object: SampleRecord
) -> None:
    assert db_object.id == domain_object.id
    assert db_object.record_data == domain_object.record_data


async def test_add_record(
    sample_record_repository: SampleRecordRepository,
    sample_record_factory: type[SampleRecordModelFactory],
    isolated_session: AsyncSession,
):
    """Test adding a new record."""

    new_record = SampleRecord(record_data="test_add")
    created_record = await sample_record_repository.create(new_record)

    count = await isolated_session.scalar(
        select(func.count()).select_from(SampleRecordModel)
    )
    assert count == 1

    diff = DeepDiff(new_record, created_record, exclude_paths={"id"})
    assert not diff, diff


async def test_update_record(
    sample_record_repository: SampleRecordRepository,
    isolated_session: AsyncSession,
    sample_record_factory: type[SampleRecordModelFactory],
):
    """Test updating an existing record."""

    existing_record = await sample_record_factory.create(record_data="test_update")

    updated_record = SampleRecord(
        id=existing_record.id, record_data="test_update_new_value"
    )
    updated_record_in_db = await sample_record_repository.update(updated_record)

    count = await isolated_session.scalar(
        select(func.count()).select_from(SampleRecordModel)
    )
    assert count == 1
    assert updated_record_in_db.id == existing_record.id
    assert updated_record_in_db.record_data == "test_update_new_value"


async def test_delete_record(
    sample_record_repository: SampleRecordRepository,
    isolated_session: AsyncSession,
    sample_record_factory: type[SampleRecordModelFactory],
):
    """Test deleting a record."""
    existing_record = await sample_record_factory.create(record_data="test_delete")
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
    """Test deleting a not existing record raises the error."""

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
