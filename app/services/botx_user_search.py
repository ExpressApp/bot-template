"""Module for user searching on cts."""

from typing import Optional, Tuple
from uuid import UUID

from pybotx import Bot, BotAccount, UserFromSearch, UserKinds, UserNotFoundError


class UserIsBotError(Exception):
    """Error for raising when found user is bot."""


async def search_user_on_each_cts(
    bot: Bot, huid: UUID
) -> Optional[Tuple[UserFromSearch, BotAccount]]:
    """Search user by huid on all cts on which bot is registered.

    return type: tuple of UserFromSearch instance and host.
    """

    for bot_account in bot.bot_accounts:
        try:
            user = await bot.search_user_by_huid(bot_id=bot_account.id, huid=huid)
        except UserNotFoundError:
            continue

        if user.user_kind == UserKinds.BOT:
            raise UserIsBotError

        return user, bot_account

    return None
