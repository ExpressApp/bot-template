import uuid

import pytest
from botx import ChatTypes

from app.db.botx.models import BotXBot, BotXChat, BotXCTS, BotXUser


class TestStringRepresentation:
    @pytest.mark.asyncio
    async def test_cts(self):
        cts = await BotXCTS.create(host="somehost")

        assert str(cts) == "<BotXCTS host: somehost>"

    @pytest.mark.asyncio
    async def test_current_bot(self):
        cts = await BotXCTS.create(host="somehost")

        bot_id = uuid.uuid4()
        bot = await BotXBot.create(bot_id=bot_id, current_bot=True, cts=cts)
        assert str(bot) == f"<BotXBot bot_id: {bot_id} current: {True}>"

    @pytest.mark.asyncio
    async def test_simple_bot(self):
        cts = await BotXCTS.create(host="somehost")

        bot_id = uuid.uuid4()
        bot = await BotXBot.create(bot_id=bot_id, cts=cts)
        assert str(bot) == f"<BotXBot bot_id: {bot_id} current: {False}>"

    @pytest.mark.asyncio
    async def test_user(self):
        cts = await BotXCTS.create(host="somehost")

        user_huid = uuid.uuid4()
        user = await BotXUser.create(user_huid=user_huid, cts=cts)
        assert str(user) == f"<BotXUser user_huid: {user_huid}>"

    @pytest.mark.asyncio
    async def test_chat(self):
        cts = await BotXCTS.create(host="somehost")

        group_chat_id = uuid.uuid4()
        chat = await BotXChat.create(
            group_chat_id=group_chat_id, chat_type=ChatTypes.chat, cts=cts
        )
        assert str(chat) == f"<BotXChat group_chat_id: {group_chat_id} chat_type: chat>"
