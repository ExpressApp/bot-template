"""Configuration for bot instance."""

from httpx import AsyncClient, Limits
from pybotx import Bot

from app.bot.commands import common
from app.bot.error_handlers.internal_error import internal_error_handler
from app.bot.middlewares.answer_error import answer_error_middleware
from app.settings import settings

BOTX_CALLBACK_TIMEOUT = 30


def get_bot() -> Bot:
    return Bot(
        collectors=[common.collector],
        bot_accounts=settings.BOT_CREDENTIALS,
        exception_handlers={Exception: internal_error_handler},
        default_callback_timeout=BOTX_CALLBACK_TIMEOUT,
        httpx_client=AsyncClient(
            timeout=60,
            limits=Limits(max_keepalive_connections=None, max_connections=None),
        ),
        middlewares=[answer_error_middleware],
    )
