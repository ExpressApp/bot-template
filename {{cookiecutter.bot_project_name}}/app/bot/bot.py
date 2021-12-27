"""Configuration for bot instance."""

from botx import Bot

from app.bot.commands import common
from app.bot.error_handlers.internal_error import internal_error_handler
from app.settings import settings

bot = Bot(
    collectors=[common.collector],
    bot_accounts=settings.BOT_CREDENTIALS,
    exception_handlers={Exception: internal_error_handler},
)
