import asyncio
from asyncio import current_task
from datetime import datetime
from http import HTTPStatus
from pathlib import Path
from typing import Any, AsyncGenerator, Callable, Dict, Generator, List, Optional
from unittest.mock import AsyncMock, patch
from uuid import UUID, uuid4
import os

import httpx
import jwt
import pytest
import respx
import sqlalchemy
from alembic import config as alembic_config, command
from alembic.config import Config
from asgi_lifespan import LifespanManager
from pybotx import (
    Bot,
    BotAccount,
    Chat,
    ChatTypes,
    IncomingMessage,
    UserDevice,
    UserSender,
)
from pybotx.logger import logger
from sqlalchemy import NullPool, event
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_scoped_session,
    async_sessionmaker,
)
from sqlalchemy.orm import sessionmaker, Session, SessionTransaction
from testcontainers.postgres import PostgresContainer

from app.infrastructure.caching.redis_repo import RedisRepo
from app.infrastructure.db.sqlalchemy import (
    build_db_session_factory,
    AsyncSessionFactory,
    make_url_async,
)
from app.infrastructure.repositories.sample_record import SampleRecordRepository
from app.main import get_application
from app.settings import settings, AppSettings
from tests.factories import SampleRecordModelFactory


@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, None, None]:
    """Starts a temporary PostgreSQL container for the test session."""
    container_name = f"bot_testing_container"

    with PostgresContainer("postgres:15").with_name(container_name) as postgres:
        container_url = postgres.get_connection_url()
        with patch.object(settings, "POSTGRES_DSN", container_url):
            yield postgres


@pytest.fixture(scope="session")
def event_loop():
    """Create a session-scoped event loop for async session-scoped fixtures."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


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
async def isolated_session(db_session_factory):
    """Isolated session with proper rollback to prevent test data leaks."""
    alembic_cfg = Config(str(Path(__file__).parent.parent / "alembic.ini"))
    command.upgrade(alembic_cfg, "head")
    async with db_session_factory() as session:
        yield session
    command.downgrade(alembic_cfg, "base")


@pytest.fixture
async def sample_record_repository(isolated_session) -> SampleRecordRepository:
    return SampleRecordRepository(isolated_session)


@pytest.fixture
def sample_record_factory(
    isolated_session,
) -> Generator[type[SampleRecordModelFactory], None, None]:
    SampleRecordModelFactory._meta.sqlalchemy_session = isolated_session
    yield SampleRecordModelFactory
    SampleRecordModelFactory._meta.sqlalchemy_session = None


@pytest.fixture
async def db_session(bot: Bot) -> AsyncGenerator[AsyncSession, None]:
    async with bot.state.db_session_factory() as session:
        yield session


@pytest.fixture
async def redis_repo(bot: Bot) -> RedisRepo:
    return bot.state.redis_repo


def mock_authorization() -> None:
    respx.route(method="GET", path__regex="/api/v2/botx/bots/.*/token").mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": "token",
            },
        ),
    )


@pytest.fixture
async def bot(
    respx_mock: Callable[..., Any],  # We can't apply pytest mark to fixture
) -> AsyncGenerator[Bot, None]:
    fastapi_app = get_application()

    mock_authorization()

    async with LifespanManager(fastapi_app):
        built_bot = fastapi_app.state.bot

        built_bot.answer_message = AsyncMock(return_value=uuid4())

        yield built_bot


@pytest.fixture
def bot_id() -> UUID:
    return settings.BOT_CREDENTIALS[0].id


@pytest.fixture
def host() -> str:
    return settings.BOT_CREDENTIALS[0].host


@pytest.fixture
def secret_key() -> str:
    return settings.BOT_CREDENTIALS[0].secret_key


@pytest.fixture
def user_huid() -> UUID:
    return UUID("cd069aaa-46e6-4223-950b-ccea42b89c06")


@pytest.fixture
def authorization_token_payload(bot_id: UUID, host: str) -> Dict[str, Any]:
    return {
        "aud": [str(bot_id)],
        "exp": datetime(year=3000, month=1, day=1).timestamp(),
        "iat": datetime(year=2000, month=1, day=1).timestamp(),
        "iss": host,
        "jti": "2uqpju31h6dgv4f41c005e1i",
        "nbf": datetime(year=2000, month=1, day=1).timestamp(),
    }


@pytest.fixture
def authorization_header(
    secret_key: str,
    authorization_token_payload: Dict[str, Any],
) -> Dict[str, str]:
    token = jwt.encode(
        payload=authorization_token_payload,
        key=secret_key,
    )
    return {"authorization": f"Bearer {token}"}


@pytest.fixture
def incoming_message_factory(
    bot_id: UUID,
    user_huid: UUID,
    host: str,
) -> Callable[..., IncomingMessage]:
    def factory(
        *,
        body: str = "",
        ad_login: Optional[str] = None,
        ad_domain: Optional[str] = None,
    ) -> IncomingMessage:
        return IncomingMessage(
            bot=BotAccount(
                id=bot_id,
                host=host,
            ),
            sync_id=uuid4(),
            source_sync_id=None,
            body=body,
            data={},
            metadata={},
            sender=UserSender(
                huid=user_huid,
                udid=None,
                ad_login=ad_login,
                ad_domain=ad_domain,
                username=None,
                is_chat_admin=True,
                is_chat_creator=True,
                device=UserDevice(
                    manufacturer=None,
                    device_name=None,
                    os=None,
                    pushes=None,
                    timezone=None,
                    permissions=None,
                    platform=None,
                    platform_package_id=None,
                    app_version=None,
                    locale=None,
                ),
            ),
            chat=Chat(
                id=uuid4(),
                type=ChatTypes.PERSONAL_CHAT,
            ),
            raw_command=None,
        )

    return factory


@pytest.fixture
def loguru_caplog(
    caplog: pytest.LogCaptureFixture,
) -> Generator[pytest.LogCaptureFixture, None, None]:
    # https://github.com/Delgan/loguru/issues/59

    handler_id = logger.add(caplog.handler, format="{message}")
    yield caplog
    logger.remove(handler_id)
