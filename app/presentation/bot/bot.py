"""Configuration for bot instance."""

from httpx import AsyncClient, Limits
from pybotx import Bot, CallbackRepoProto

from app.presentation.bot.middlewares.answer_error import answer_error_middleware
from app.presentation.bot.middlewares.smart_logger import smart_logger_middleware
from app.presentation.bot.commands import common, sample_record
from app.presentation.bot.error_handlers.internal_error_handler import internal_error_handler
from app.settings import settings


def get_bot(callback_repo: CallbackRepoProto) -> Bot:
    exception_handlers = {}
    if not settings.RAISE_BOT_EXCEPTIONS:
        exception_handlers[Exception] = internal_error_handler

    return Bot(
        collectors=[common.collector, sample_record.collector],
        bot_accounts=settings.BOT_CREDENTIALS,
        exception_handlers=exception_handlers,  # type: ignore
        default_callback_timeout=settings.BOTX_CALLBACK_TIMEOUT_IN_SECONDS,
        httpx_client=AsyncClient(
            timeout=60,
            limits=Limits(max_keepalive_connections=None, max_connections=None),
        ),
        middlewares=[
            smart_logger_middleware,
            answer_error_middleware,
        ],
        callback_repo=callback_repo,
    )
