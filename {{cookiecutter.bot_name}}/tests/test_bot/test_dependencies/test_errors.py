import logging

import pytest
from botx import Message, TestClient
from botx.testing import MessageBuilder

from app.bot.dependencies.errors import internal_error_handler


@pytest.mark.asyncio
async def test_send_error_message_to_user(
    caplog, builder: MessageBuilder, botx_client: TestClient
):
    caplog.set_level(logging.DEBUG)
    exc = Exception("custom error")
    msg = Message.from_dict(builder.message.dict(), botx_client.bot)

    with pytest.raises(Exception):
        await internal_error_handler(exc, msg)

    assert botx_client.notifications[0]
