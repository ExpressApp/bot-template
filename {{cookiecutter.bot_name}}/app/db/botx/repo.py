"""Repository for botx models."""
from uuid import UUID

from botx import ChatTypes

from app.db.botx.models import BotXBot, BotXChat, BotXCTS, BotXUser


async def get_user_by_huid(huid: UUID) -> BotXUser:
    """Get botx user by huid."""
    return await BotXUser.get(user_huid=huid)


async def get_cts_of_user_by_huid(huid: UUID) -> BotXCTS:
    """Get user's cts by huid."""
    return await BotXCTS.get(users__user_huid=huid)


async def get_personal_chat_for_user(user_huid: UUID) -> BotXChat:
    """Get personal chat with user by huid."""
    return await BotXChat.get(
        members__user_huid=user_huid,
        cts__bots__current_bot=True,
        chat_type=ChatTypes.chat,
    )


async def get_cts_of_current_bot_by_host(host: str) -> BotXCTS:
    """Get current bot's cts by host."""
    return await BotXCTS.get(host=host, bots__current_bot=True)


async def get_current_bot_by_host(host: str) -> BotXBot:
    """Get current bot by host."""
    return await BotXBot.get(cts_id=host, current_bot=True)
