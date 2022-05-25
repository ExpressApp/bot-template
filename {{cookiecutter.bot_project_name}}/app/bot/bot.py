"""Configuration for bot instance."""
from typing import Optional

from httpx import AsyncClient, Limits
from pybotx import Bot, CallbackRepoProto

from app.bot.commands import common
from app.bot.error_handlers.internal_error import internal_error_handler
from app.bot.middlewares.answer_error import answer_error_middleware
from app.settings import settings

BOTX_CALLBACK_TIMEOUT = 30


def get_bot(
    add_internal_error_handler: bool,
    callback_repo: Optional[CallbackRepoProto] = None,
) -> Bot:
    exception_handlers = {}
    if add_internal_error_handler:
        exception_handlers[Exception] = internal_error_handler

    return Bot(
        collectors=[common.collector],
        bot_accounts=settings.BOT_CREDENTIALS,
        exception_handlers=exception_handlers,  # type: ignore
        default_callback_timeout=BOTX_CALLBACK_TIMEOUT,
        httpx_client=AsyncClient(
            timeout=60,
            limits=Limits(max_keepalive_connections=None, max_connections=None),
        ),
        middlewares=[answer_error_middleware],
        callback_repo=callback_repo,
    )
