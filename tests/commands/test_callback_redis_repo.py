import asyncio
import os
from http import HTTPStatus
from typing import AsyncGenerator, Callable

import httpx
import pytest
from asgi_lifespan import LifespanManager
from pybotx import (
    Bot,
    BotXMethodFailedCallbackReceivedError,
    CallbackNotReceivedError,
    IncomingMessage,
    lifespan_wrapper,
)
from redis import asyncio as aioredis
from respx import MockRouter

from app.caching.callback_redis_repo import CallbackRedisRepo
from app.main import get_application
from app.settings import settings
from tests.conftest import mock_authorization

pytestmark = pytest.mark.xfail(
    os.getenv("CI") == "true", reason="CI is too slow for this tests"
)


@pytest.fixture
async def bot() -> AsyncGenerator[Bot, None]:
    redis_repo = CallbackRedisRepo(aioredis.from_url(settings.REDIS_DSN))
    fastapi_app = get_application(
        add_internal_error_handler=False, callback_repo=redis_repo
    )
    built_bot = fastapi_app.state.bot

    for bot_account in built_bot.bot_accounts:
        mock_authorization(bot_account.host, bot_account.id)

    async with LifespanManager(fastapi_app):
        yield built_bot


async def test_callback_redis_repo_successful_callback(
    respx_mock: MockRouter,
    host: str,
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
) -> None:
    # - Arrange -
    message = incoming_message_factory(body="/_test-redis-callback-repo")
    respx_mock.post(
        f"https://{host}/api/v4/botx/notifications/direct",
        json={
            "group_chat_id": str(message.chat.id),
            "notification": {"status": "ok", "body": "Hello!"},
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
            },
        ),
    )

    # - Act -
    async with lifespan_wrapper(bot):
        task = bot.async_execute_bot_command(message)
        await asyncio.sleep(0)

        await bot.set_raw_botx_method_result(
            {
                "status": "ok",
                "sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
                "result": {},
            }
        )
        await asyncio.sleep(0)

        await task

    # - Assert -
    assert task.exception() is None


async def test_callback_redis_repo_unsuccessful_callback(
    respx_mock: MockRouter,
    host: str,
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
) -> None:
    # - Arrange -
    message = incoming_message_factory(body="/_test-redis-callback-repo")
    respx_mock.post(
        f"https://{host}/api/v4/botx/notifications/direct",
        json={
            "group_chat_id": str(message.chat.id),
            "notification": {"status": "ok", "body": "Hello!"},
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
            },
        ),
    )

    # - Act -
    async with lifespan_wrapper(bot):
        task = bot.async_execute_bot_command(message)
        await asyncio.sleep(0)

        await bot.set_raw_botx_method_result(
            {
                "status": "error",
                "sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
                "reason": "test_reason",
                "errors": [],
                "error_data": {},
            }
        )
        with pytest.raises(BotXMethodFailedCallbackReceivedError) as exc:
            await task

    # - Assert -
    assert "test_reason" in str(exc.value)  # noqa: WPS441


async def test_callback_redis_repo_no_callback(
    respx_mock: MockRouter,
    host: str,
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
) -> None:
    # - Arrange -
    message = incoming_message_factory(body="/_test-redis-callback-repo")
    respx_mock.post(
        f"https://{host}/api/v4/botx/notifications/direct",
        json={
            "group_chat_id": str(message.chat.id),
            "notification": {"status": "ok", "body": "Hello!"},
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
            },
        ),
    )

    # - Act -
    async with lifespan_wrapper(bot):
        task = bot.async_execute_bot_command(message)

        with pytest.raises(CallbackNotReceivedError) as exc:
            await task

    # - Assert -
    assert "hasn't been received" in str(exc.value)  # noqa: WPS441


async def test_callback_redis_repo_wait_callback(
    respx_mock: MockRouter,
    host: str,
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
) -> None:
    # - Arrange -
    message = incoming_message_factory(body="/_test-redis-callback-repo-wait")
    respx_mock.post(
        f"https://{host}/api/v4/botx/notifications/direct",
        json={
            "group_chat_id": str(message.chat.id),
            "notification": {"status": "ok", "body": "Hello!"},
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
            },
        ),
    )

    # - Act -
    async with lifespan_wrapper(bot):
        task = bot.async_execute_bot_command(message)
        await asyncio.sleep(0.1)

        await bot.set_raw_botx_method_result(
            {
                "status": "error",
                "sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
                "reason": "test_reason",
                "errors": [],
                "error_data": {},
            }
        )
        await asyncio.sleep(0.1)

        await task

    # - Assert -
    assert task.exception() is None


async def test_callback_redis_repo_no_wait_callback(
    respx_mock: MockRouter,
    host: str,
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    loguru_caplog: pytest.LogCaptureFixture,
) -> None:
    # - Arrange -
    message = incoming_message_factory(body="/_test-redis-callback-repo-no-wait")
    respx_mock.post(
        f"https://{host}/api/v4/botx/notifications/direct",
        json={
            "group_chat_id": str(message.chat.id),
            "notification": {"status": "ok", "body": "Hello!"},
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
            },
        ),
    )

    # - Act -
    async with lifespan_wrapper(bot):
        await bot.async_execute_bot_command(message)

    # - Assert -
    assert (
        "Callback `21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3` wasn't waited"
        in loguru_caplog.text
    )
