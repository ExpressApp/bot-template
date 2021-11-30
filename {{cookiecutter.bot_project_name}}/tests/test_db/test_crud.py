import warnings

import pytest
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.db.crud import CRUD
from app.db.models import RecordModel
from app.db.sqlalchemy import AsyncSessionFactory, Base, make_url_async
from app.schemas.domains import Record
from app.settings.environments.test import TestAppSettings


@pytest.fixture
async def session_factory(settings: TestAppSettings) -> AsyncSessionFactory:
    warnings.filterwarnings("ignore", category=ResourceWarning)
    engine = create_async_engine(
        make_url_async(settings.POSTGRES_DSN), echo=settings.SQL_DEBUG
    )
    session_factory = sessionmaker(
        bind=engine, expire_on_commit=False, class_=AsyncSession
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield session_factory
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def record_data() -> dict[str, str]:
    return {"record_data": "random text"}


@pytest.fixture
def record_data2() -> dict[str, str]:
    return {"record_data": "222 random text"}


@pytest.fixture
async def record(session_factory: AsyncSessionFactory, record_data) -> Record:
    async with session_factory() as session, session.begin():
        await CRUD.create(session, RecordModel, record_data)
        record = await CRUD.get(session, RecordModel, 1)
    return Record.from_orm(record)


@pytest.mark.db
@pytest.mark.asyncio
async def test_crud_create(
    session_factory: AsyncSessionFactory, record_data: dict[str, str]
):
    async with session_factory() as session, session.begin():
        result = await CRUD.create(session, RecordModel, record_data)
        assert result == (1,)


@pytest.mark.db
@pytest.mark.asyncio
async def test_crud_update(
    session_factory: AsyncSessionFactory,
    record: Record,
    record_data: dict[str, str],
    record_data2: dict[str, str],
):
    async with session_factory() as session, session.begin():
        record = await CRUD.get(session, RecordModel, record.id)
        assert record.record_data == record_data["record_data"]

        await CRUD.update(session, RecordModel, record.id, record_data2)
        updated_record = await CRUD.get(session, RecordModel, record.id)
        assert updated_record.record_data == record_data2["record_data"]


@pytest.mark.db
@pytest.mark.asyncio
async def test_crud_delete(session_factory: AsyncSessionFactory, record: Record):
    async with session_factory() as session, session.begin():
        records = await CRUD.all(session, RecordModel)
        assert len(records) == 1

        await CRUD.delete(session, RecordModel, record.id)
        records = await CRUD.all(session, RecordModel)
        assert len(records) == 0


@pytest.mark.db
@pytest.mark.asyncio
async def test_crud_get_existing(session_factory: AsyncSessionFactory, record: Record):
    async with session_factory() as session, session.begin():
        result = await CRUD.get(session, RecordModel, record.id)
        assert result.id == record.id


@pytest.mark.db
@pytest.mark.asyncio
async def test_crud_get_not_existing(
    session_factory: AsyncSessionFactory, record: Record
):
    async with session_factory() as session, session.begin():
        with pytest.raises(NoResultFound):
            await CRUD.get(session, RecordModel, 2)


@pytest.mark.db
@pytest.mark.asyncio
async def test_crud_get_or_none(session_factory: AsyncSessionFactory, record: Record):
    async with session_factory() as session, session.begin():
        result = await CRUD.get(session, RecordModel, record.id)
        assert result.id == record.id


@pytest.mark.db
@pytest.mark.asyncio
async def test_crud_get_or_none(session_factory: AsyncSessionFactory):
    async with session_factory() as session, session.begin():
        result = await CRUD.get_or_none(session, RecordModel, 2)
        assert result is None
