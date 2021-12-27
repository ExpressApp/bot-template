"""Module for user searching on cts."""

from typing import Optional
from uuid import UUID

from botx import Bot, BotAccount, UserFromSearch, UserNotFoundError


class UserIsBotError(Exception):
    """Error for raising when found user is bot."""


async def search_user_on_each_cts(
    bot: Bot, huid: UUID
) -> Optional[tuple[UserFromSearch, BotAccount]]:
    """Search user by huid on all cts on which bot is registered.

    return type: tuple of UserFromSearch instance and host.
    """

    for bot_account in bot.bot_accounts:
        try:
            user = await bot.search_user_by_huid(bot_id=bot_account.id, huid=huid)
        except UserNotFoundError:
            continue

        name = user.name.lower()
        if name.endswith("bot") or name.endswith("бот"):  # TODO: user_kind
            raise UserIsBotError()

        return user, bot_account

    return None
