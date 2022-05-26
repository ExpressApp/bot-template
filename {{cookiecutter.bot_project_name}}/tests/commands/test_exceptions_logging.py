import json
from http import HTTPStatus
from typing import Awaitable, Callable

import httpx
import pytest
from pybotx import Bot, IncomingMessage
from pybotx.models.commands import BotCommand
from respx import MockRouter


async def test__http_exception__correct_logs(
    respx_mock: MockRouter,
    host: str,
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    execute_bot_command: Callable[[Bot, BotCommand], Awaitable[None]],
    loguru_caplog: pytest.LogCaptureFixture,
) -> None:
    message = incoming_message_factory(body="/_test-http-exception-correct-logs")
    response = {
        "error_data": {"recipients": "invalid"},
        "errors": [],
        "reason": "malformed_request",
        "status": "error",
    }
    respx_mock.post(
        f"https://{host}/api/v4/botx/notifications/direct",
        json={
            "group_chat_id": str(message.chat.id),
            "notification": {"body": "Hello!", "status": "ok"},
            "recipients": "all",
        },
    ).mock(
        return_value=httpx.Response(
            status_code=HTTPStatus.BAD_REQUEST,
            content=json.dumps(response).encode("utf-8"),
        )
    )

    # - Act -
    await execute_bot_command(bot, message)

    # - Assert -
    assert "Logging error in Loguru Handler" not in loguru_caplog.text
    assert "failed with code 400 and payload:" in loguru_caplog.text


async def test__callback_exception__correct_logs(
    respx_mock: MockRouter,
    host: str,
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    execute_bot_command: Callable[[Bot, BotCommand], Awaitable[None]],
    loguru_caplog: pytest.LogCaptureFixture,
) -> None:
    # - Arrange -
    message = incoming_message_factory(body="/_test-callback-exception-correct-logs")
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
    await execute_bot_command(bot, message)

    # - Assert -
    assert "Logging error in Loguru Handler" not in loguru_caplog.text
    assert "BotXMethodFailedCallbackReceivedError" in loguru_caplog.text
