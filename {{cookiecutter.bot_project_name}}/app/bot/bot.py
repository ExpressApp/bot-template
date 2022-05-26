"""Configuration for bot instance."""
from typing import Optional

from httpx import AsyncClient, Limits
from pybotx import Bot, CallbackRepoProto
from pybotx_smart_logger import (
    BotXSmartLoggerMiddleware,
    make_smart_logger_exception_handler,
)

from app.bot.commands import common
from app.bot.middlewares.answer_error import answer_error_middleware
from app.resources import strings
from app.settings import settings

BOTX_CALLBACK_TIMEOUT = 30

smart_logger_exception_handler = make_smart_logger_exception_handler(
    strings.SOMETHING_GOES_WRONG
)


def get_bot(
    add_internal_error_handler: bool,
    callback_repo: Optional[CallbackRepoProto] = None,
) -> Bot:
    exception_handlers = {}
    if add_internal_error_handler:
        exception_handlers[Exception] = smart_logger_exception_handler

    return Bot(
        collectors=[common.collector],
        bot_accounts=settings.BOT_CREDENTIALS,
        exception_handlers=exception_handlers,  # type: ignore
        default_callback_timeout=BOTX_CALLBACK_TIMEOUT,
        httpx_client=AsyncClient(
            timeout=60,
            limits=Limits(max_keepalive_connections=None, max_connections=None),
        ),
        middlewares=[
            answer_error_middleware,
            BotXSmartLoggerMiddleware(debug_enabled_for_message=True).dispatch,
        ],
        callback_repo=callback_repo,
    )
