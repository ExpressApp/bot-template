"""Configuration for bot instance."""

from pybotx import Bot

from app.bot.commands import common
from app.bot.error_handlers.internal_error import internal_error_handler
from app.settings import settings

BOTX_CALLBACK_TIMEOUT = 30


def get_bot() -> Bot:
    return Bot(
        collectors=[common.collector],
        bot_accounts=settings.BOT_CREDENTIALS,
        exception_handlers={Exception: internal_error_handler},
        default_callback_timeout=BOTX_CALLBACK_TIMEOUT,
    )
