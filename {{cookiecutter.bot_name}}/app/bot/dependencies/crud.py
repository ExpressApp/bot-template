"""Crud functions for usage in commands like dependencies."""
from botx import CommandTypes, Message, SystemEvents, UserKinds

from app.db.botx.models import BotXBot, BotXChat, BotXCTS, BotXUser


async def auto_models_update(message: Message) -> None:
    """Save or update information about user(s), chat and cts."""
    cts, _ = await BotXCTS.get_or_create(host=message.host)
    chat, _ = await BotXChat.get_or_create(
        group_chat_id=message.group_chat_id,
        defaults={"chat_type": message.chat_type, "cts": cts},
    )

    current_bot, _ = await BotXBot.get_or_create(
        bot_id=message.bot_id, defaults={"current_bot": True, "cts": cts}
    )

    chat.last_sync_id = message.sync_id
    await chat.save()

    if message.command.command_type == CommandTypes.system:
        if message.command.body == SystemEvents.chat_created.value:
            await _update_chat_members(message, cts, chat)
    else:
        await _update_user_info(message, cts, chat)


async def _update_user_info(message: Message, cts: BotXCTS, chat: BotXChat) -> None:
    """Create or update user's huid, username, login, domain and role in chat."""
    bot_user, _ = await BotXUser.get_or_create(
        user_huid=message.user_huid, defaults={"cts": cts}
    )
    if message.user.username:
        bot_user.username = message.user.username
        bot_user.ad_login = message.user.ad_login.lower()
        bot_user.ad_domain = message.user.ad_domain.lower()
        await bot_user.save()

    if message.user.is_creator:
        chat.creator = bot_user
        await chat.save()

    if message.user.is_admin:
        await bot_user.administered_chats.add(chat)
    else:
        await chat.admins.remove(bot_user)

    await chat.members.add(bot_user)


async def _update_chat_members(message: Message, cts: BotXCTS, chat: BotXChat) -> None:
    """Create or update chat's admins, creator and other members (users and bots)."""
    for user in message.command.data.members:
        if user.user_kind in {UserKinds.user, UserKinds.cts_user}:
            bot_user, _ = await BotXUser.get_or_create(
                user_huid=user.huid,
                defaults={"username": user.name, "cts": cts},
            )
            await chat.members.add(bot_user)

            if user.admin:
                await chat.admins.add(bot_user)

            if user.huid == message.command.data.creator:
                chat.creator = bot_user
                await chat.save()

        else:
            bot, _ = await BotXBot.get_or_create(
                bot_id=user.huid, defaults={"cts": cts}
            )
            bot.name = user.name
            await bot.save()
