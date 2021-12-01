import warnings
from typing import Any

import pytest
from sqlalchemy import insert, select
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
async def record(
    session_factory: AsyncSessionFactory, record_data: dict[str, str]
) -> Record:
    async with session_factory() as session, session.begin():
        query = insert(RecordModel).values(**record_data)
        await session.execute(query)

        query = select(RecordModel)
        rows = await session.execute(query)
        record = rows.scalars().one()

    return Record.from_orm(record)


async def get_record(session: AsyncSession, pk_val: Any) -> Record:
    query = select(RecordModel).where(RecordModel.id == pk_val)
    rows = await session.execute(query)
    record_in_db = rows.scalars().one()
    return Record.from_orm(record_in_db)


async def get_all_records(session: AsyncSession) -> list[Record]:
    query = select(RecordModel)
    rows = await session.execute(query)
    records_in_db = rows.scalars().all()
    return [Record.from_orm(record) for record in records_in_db]


@pytest.mark.db
@pytest.mark.asyncio
async def test_crud_create(
    session_factory: AsyncSessionFactory, record_data: dict[str, str]
):
    async with session_factory() as session, session.begin():
        crud = CRUD(session, RecordModel)
        result = await crud.create(model_data=record_data)
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
        record_from_db = await get_record(session=session, pk_val=record.id)
        assert record_from_db.record_data == record_data["record_data"]

        crud = CRUD(session, RecordModel)
        await crud.update(pkey_val=record.id, model_data=record_data2)
        updated_record = await get_record(session=session, pk_val=record.id)
        assert updated_record.record_data == record_data2["record_data"]


@pytest.mark.db
@pytest.mark.asyncio
async def test_crud_delete(session_factory: AsyncSessionFactory, record: Record):
    async with session_factory() as session, session.begin():
        records = await get_all_records(session)
        assert len(records) == 1

        crud = CRUD(session, RecordModel)
        await crud.delete(pkey_val=record.id)
        records = await get_all_records(session)
        assert len(records) == 0


@pytest.mark.db
@pytest.mark.asyncio
async def test_crud_get_existing(session_factory: AsyncSessionFactory, record: Record):
    async with session_factory() as session, session.begin():
        crud = CRUD(session, RecordModel)
        result = await crud.get(pkey_val=record.id)
        assert result.id == record.id


@pytest.mark.db
@pytest.mark.asyncio
async def test_crud_get_not_existing(
    session_factory: AsyncSessionFactory, record: Record
):
    async with session_factory() as session, session.begin():
        with pytest.raises(NoResultFound):
            crud = CRUD(session, RecordModel)
            await crud.get(pkey_val=2)


@pytest.mark.db
@pytest.mark.asyncio
async def test_crud_get_or_none_not_existing(session_factory: AsyncSessionFactory):
    async with session_factory() as session, session.begin():
        crud = CRUD(session, RecordModel)
        result = await crud.get_or_none(pkey_val=2)
        assert result is None


@pytest.mark.db
@pytest.mark.asyncio
async def test_crud_get_or_none_existing(
    session_factory: AsyncSessionFactory, record: Record
):
    async with session_factory() as session, session.begin():
        crud = CRUD(session, RecordModel)
        result = await crud.get_or_none(pkey_val=record.id)
        assert result.id == record.id
