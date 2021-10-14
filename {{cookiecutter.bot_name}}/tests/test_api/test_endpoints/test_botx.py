import uuid

import pytest
from botx import Bot, ChatTypes
from botx.models.status import StatusRecipient
from botx.testing import MessageBuilder
from fastapi import FastAPI
from httpx import AsyncClient, codes


@pytest.mark.asyncio
async def test_botx_status_endpoint_return_right_bot_status(
    app: FastAPI, http_client: AsyncClient, bot: Bot
):
    url = app.url_path_for("botx:status")
    recipient = StatusRecipient(
        bot_id=uuid.uuid4(), user_huid=uuid.uuid4(), chat_type=ChatTypes.chat
    ).dict()
    recipient.update({"chat_type": f"{ChatTypes.chat.value}"})
    response = await http_client.get(url, params=recipient)
    assert response.status_code == codes.OK
    assert response.json() == await bot.status()


@pytest.mark.asyncio
@pytest.mark.parametrize("is_admin", [True, False, None])
async def test_send_status_with_missing_optional_fields(
    app: FastAPI, http_client: AsyncClient, bot: Bot, is_admin
):
    url = app.url_path_for("botx:status")
    recipient = StatusRecipient(
        bot_id=uuid.uuid4(),
        user_huid=uuid.uuid4(),
        chat_type=ChatTypes.chat,
        is_admin=is_admin,
    ).dict(exclude_none=True)
    recipient.update({"chat_type": f"{ChatTypes.chat.value}"})
    response = await http_client.get(url, params=recipient)
    assert response.status_code == codes.OK
    assert response.json() == await bot.status()


@pytest.mark.asyncio
async def test_botx_command_endpoint_return_accepted(
    app: FastAPI, http_client: AsyncClient, builder: MessageBuilder
):
    text = "/help"
    builder.body = text
    url = app.url_path_for("botx:command")
    response = await http_client.post(url, data=builder.message.json())

    assert response.status_code == codes.ACCEPTED
