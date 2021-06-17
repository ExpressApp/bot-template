import pytest
from botx import Bot, ChatCreatedEvent, Message, SystemEvents
from botx.testing import MessageBuilder

from app.bot.dependencies.crud import auto_models_update
from app.db.botx.models import BotXBot, BotXChat, BotXCTS, BotXUser


class TestAutoModelsUpdate:
    @pytest.mark.asyncio
    async def test_with_user_in_personal_chat(self, builder: MessageBuilder, bot: Bot):
        builder.user.is_admin = True
        builder.user.is_creator = True
        msg = Message.from_dict(builder.message.dict(), bot)

        await auto_models_update(msg)

        user: BotXUser = await BotXUser.get(user_huid=msg.user_huid)
        await BotXChat.get(group_chat_id=msg.group_chat_id)
        await BotXBot.get(bot_id=msg.bot_id)
        await BotXCTS.get(host=msg.host)

        assert await user.administered_chats.filter(
            group_chat_id=msg.group_chat_id
        ).first()
        assert await user.created_chats.filter(group_chat_id=msg.group_chat_id).first()
        assert await user.chats.filter(group_chat_id=msg.group_chat_id).first()

    @pytest.mark.asyncio
    async def test_user_that_is_no_admin(self, builder: MessageBuilder, bot: Bot):
        builder.user.is_admin = True
        msg = Message.from_dict(builder.message.dict(), bot)

        await auto_models_update(msg)

        user: BotXUser = await BotXUser.get(user_huid=msg.user_huid)

        assert await user.administered_chats.filter(
            group_chat_id=msg.group_chat_id
        ).first()

        msg.user.is_admin = False
        await auto_models_update(msg)

        assert not await user.administered_chats.filter(
            group_chat_id=msg.group_chat_id
        ).first()

    @pytest.mark.asyncio
    async def test_chat_created(
        self, builder: MessageBuilder, bot: Bot, chat_created_data: ChatCreatedEvent
    ):
        builder.command_data = chat_created_data.dict()
        builder.body = SystemEvents.chat_created.value
        builder.user.user_huid = None
        builder.user.ad_login = None
        builder.user.ad_domain = None
        builder.user.username = None

        builder.system_command = True
        msg = Message.from_dict(builder.message.dict(), bot)

        await auto_models_update(msg)
