"""Module for user searching on cts."""

from typing import List, Tuple
from uuid import UUID

from botx import Bot, SendingCredentials
from botx.clients.methods.errors.user_not_found import UserNotFoundError
from botx.models.users import UserFromSearch

from app.settings.environments.base import BotAccount


class UserIsBotError(Exception):
    """Error for raising when found user is bot."""


async def search_user_on_each_cts(
    bot: Bot, user_huid: UUID, bot_accounts: List[BotAccount]
) -> Tuple[UserFromSearch, str]:
    """Search user by huid on all cts on which bot is registered.

    return type: tuple of UserFromSearch instance and host.
    """
    for server in bot_accounts:
        credentials = SendingCredentials(host=server.host, bot_id=server.bot_id)
        try:
            user = await bot.search_user(credentials, user_huid=user_huid)
        except UserNotFoundError:
            continue

        name = user.name.lower()
        if name.endswith("bot") or name.endswith("бот"):  # TODO: user_kind
            raise UserIsBotError()

        return user, server.host

    raise UserNotFoundError
