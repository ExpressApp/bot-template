"""Configuration for bot instance."""

from httpx import AsyncClient, Limits
from pybotx import Bot, CallbackRepoProto, IncomingMessage
from pybotx_smart_logger import (
    BotXSmartLoggerMiddleware,
    make_smart_logger_exception_handler,
)

from app.bot.commands import common
from app.bot.middlewares.answer_error import answer_error_middleware
from app.resources import strings
from app.settings import settings

BOTX_CALLBACK_TIMEOUT = 30


async def is_enabled_debug(message: IncomingMessage) -> bool:
    return message.sender.huid in settings.SMARTLOG_DEBUG_HUIDS


def get_bot(callback_repo: CallbackRepoProto, raise_exceptions: bool) -> Bot:
    exception_handlers = {}
    if not raise_exceptions:
        exception_handlers[Exception] = make_smart_logger_exception_handler(
            strings.SOMETHING_GOES_WRONG
        )

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
            BotXSmartLoggerMiddleware(
                debug_enabled_for_message=is_enabled_debug
            ).dispatch,
        ],
        callback_repo=callback_repo,
    )
