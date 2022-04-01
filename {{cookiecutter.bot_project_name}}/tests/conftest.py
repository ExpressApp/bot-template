from http import HTTPStatus
from typing import Any, AsyncGenerator, Awaitable, Callable, Generator, List, Optional
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import httpx
import pytest
import respx
from alembic import config as alembic_config
from asgi_lifespan import LifespanManager
from pybotx import (
    Bot,
    BotAccount,
    Chat,
    ChatTypes,
    IncomingMessage,
    UserDevice,
    UserSender,
    lifespan_wrapper,
)
from pybotx.models.commands import BotCommand
from sqlalchemy.ext.asyncio import AsyncSession

from app.caching.redis_repo import RedisRepo
from app.main import get_application
from app.settings import settings


@pytest.fixture
def db() -> Generator:
    alembic_config.main(argv=["upgrade", "head"])
    yield
    alembic_config.main(argv=["downgrade", "base"])


@pytest.fixture
async def db_session(bot: Bot) -> AsyncSession:
    async with bot.state.db_session_factory() as session:
        yield session


@pytest.fixture
async def redis_repo(bot: Bot) -> RedisRepo:
    return bot.state.redis_repo


@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(items: List[pytest.Function]) -> None:
    for item in items:
        if item.get_closest_marker("db"):
            item.fixturenames = ["db"] + item.fixturenames


def mock_authorization(
    host: str,
    bot_id: UUID,
) -> None:
    respx.get(f"https://{host}/api/v2/botx/bots/{bot_id}/token",).mock(
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
    built_bot = fastapi_app.state.bot

    for bot_account in built_bot.bot_accounts:
        mock_authorization(bot_account.host, bot_account.id)

    built_bot.answer_message = AsyncMock(return_value=uuid4())

    async with LifespanManager(fastapi_app):
        yield built_bot


@pytest.fixture
def bot_id() -> UUID:
    return settings.BOT_CREDENTIALS[0].id


@pytest.fixture
def host() -> str:
    return settings.BOT_CREDENTIALS[0].host


@pytest.fixture
def user_huid() -> UUID:
    return UUID("cd069aaa-46e6-4223-950b-ccea42b89c06")


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
async def execute_bot_command() -> Callable[[Bot, BotCommand], Awaitable[None]]:
    async def executor(
        bot: Bot,
        command: BotCommand,
    ) -> None:
        async with lifespan_wrapper(bot):
            bot.async_execute_bot_command(command)

    return executor
