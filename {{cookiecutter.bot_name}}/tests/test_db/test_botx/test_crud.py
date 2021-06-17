import uuid

import pytest
from botx import ChatTypes

from app.db.botx.models import BotXBot, BotXChat, BotXCTS, BotXUser
from app.db.botx.repo import (
    get_cts_of_current_bot_by_host,
    get_cts_of_user_by_huid,
    get_current_bot_by_host,
    get_personal_chat_for_user,
    get_user_by_huid,
)


@pytest.mark.asyncio
async def test_get_user_by_huid():
    cts = await BotXCTS.create(host="host")

    huid = uuid.uuid4()
    user = await BotXUser.create(user_huid=huid, cts=cts)

    assert await get_user_by_huid(huid) == user


@pytest.mark.asyncio
async def test_get_user_cts_by_huid():
    cts = await BotXCTS.create(host="host")

    huid = uuid.uuid4()
    await BotXUser.create(user_huid=huid, cts=cts)

    assert await get_cts_of_user_by_huid(huid) == cts


@pytest.mark.asyncio
async def test_get_personal_chat_for_user():
    cts = await BotXCTS.create(host="host")

    huid, bot_id, chat_id = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()

    await BotXBot.create(bot_id=bot_id, current_bot=True, cts=cts)
    user = await BotXUser.create(user_huid=huid, cts=cts)
    chat = await BotXChat.create(
        group_chat_id=chat_id, chat_type=ChatTypes.chat, cts=cts
    )
    await chat.members.add(user)

    assert await get_personal_chat_for_user(huid) == chat


@pytest.mark.asyncio
async def test_get_current_bot_by_cts_host():
    cts = await BotXCTS.create(host="host")

    bot_id = uuid.uuid4()
    await BotXBot.create(bot_id=bot_id, current_bot=True, cts=cts)

    assert await get_cts_of_current_bot_by_host(cts.host) == cts


@pytest.mark.asyncio
async def test_get_current_bot_by_host():
    botx: BotXBot
    cts = await BotXCTS.create(host="test")
    bot = await BotXBot.create(
        bot_id=uuid.uuid4(), name="test", current_bot=True, cts=cts
    )
    assert await get_current_bot_by_host(cts.host) == bot
