import re
from asyncio import current_task
from http import HTTPStatus
from pathlib import Path
from typing import Generator, Callable, Any, AsyncGenerator
from unittest.mock import patch, AsyncMock
from uuid import uuid4

import httpx
import pytest
import respx
from alembic import command
from alembic.config import Config
from asgi_lifespan import LifespanManager
from pybotx import Bot
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
    async_scoped_session,
    AsyncSession,
)
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

import app.infrastructure.db.sqlalchemy
from app.infrastructure.db.sqlalchemy import AsyncSessionFactory, make_url_async
from app.infrastructure.repositories.sample_record import SampleRecordRepository
from app.main import get_application
from app.settings import settings
from tests.integration.factories import SampleRecordModelFactory


@pytest.fixture
def sample_record_factory(
    isolated_session,
) -> Generator[type[SampleRecordModelFactory], None, None]:
    SampleRecordModelFactory._meta.sqlalchemy_session = isolated_session
    yield SampleRecordModelFactory
    SampleRecordModelFactory._meta.sqlalchemy_session = None


@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, None, None]:
    """Starts a temporary PostgreSQL container for the test session."""
    container_name = "bot_testing_container"

    with PostgresContainer("postgres:15").with_name(container_name) as postgres:
        container_url = postgres.get_connection_url()
        with patch.object(settings, "POSTGRES_DSN", container_url):
            yield postgres


@pytest.fixture(scope="session")
def redis_container() -> Generator[RedisContainer, None, None]:
    """Starts a temporary Redis container for the test session."""
    container_name = "bot_testing_redis_container"

    with RedisContainer("redis").with_name(container_name) as redis:
        container_url = (
            f"redis://{redis.get_container_host_ip()}:{redis.get_exposed_port(6379)}/0"
        )
        with patch.object(settings, "REDIS_DSN", container_url):
            yield redis


@pytest.fixture(scope="session")
async def db_session_factory(postgres_container) -> AsyncSessionFactory:
    engine: AsyncEngine = create_async_engine(
        make_url_async(settings.POSTGRES_DSN), poolclass=NullPool
    )

    factory = async_scoped_session(
        sessionmaker(
            bind=engine,
            expire_on_commit=False,
            class_=AsyncSession,  # type:ignore
        ),
        scopefunc=current_task,
    )
    return factory


@pytest.fixture
def alembic_configuration() -> Config:
    return Config(str(Path(__file__).parent.parent.parent / "alembic.ini"))


@pytest.fixture
async def isolated_session(
    db_session_factory: AsyncSessionFactory, alembic_configuration: Config
):
    command.upgrade(alembic_configuration, "head")
    async with db_session_factory() as session:
        yield session
    command.downgrade(alembic_configuration, "base")


@pytest.fixture
def override_session_factory(isolated_session):
    with patch(
        "app.infrastructure.db.sqlalchemy.get_session_factory",
        return_value=AsyncMock(return_value=isolated_session),
    ):
        yield


@pytest.fixture
async def sample_record_repository(isolated_session) -> SampleRecordRepository:
    return SampleRecordRepository(isolated_session)


def mock_authorization() -> None:
    respx.get(
        url__regex=re.compile(r"^https://[^/]+/api/v2/botx/bots/[^/]+/token(\?.*)?$")
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": "token",
            },
        ),
    )


@pytest.fixture
async def fastapi_app(
    respx_mock: Callable[..., Any],  # We can't apply pytest mark to fixture
    redis_container,
    postgres_container,
    override_session_factory,
):
    fastapi_app = get_application()
    mock_authorization()
    async with LifespanManager(fastapi_app):
        yield fastapi_app


@pytest.fixture
async def bot(
    respx_mock: Callable[..., Any],  # We can't apply pytest mark to fixture
    fastapi_app,
) -> AsyncGenerator[Bot, None]:
    with patch.object(
        Bot, "answer_message", new_callable=AsyncMock
    ) as mocked_answer_message:
        mocked_answer_message.return_value = uuid4()
        yield fastapi_app.state.bot
