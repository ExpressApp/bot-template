"""Middlewares to log all requests using smart logger wrapper."""

from pybotx import Bot, IncomingMessage, IncomingMessageHandlerFunc
from pybotx_smart_logger.wrapper import wrap_smart_logger

from app.services.log_formatters import format_raw_command
from app.settings import settings


def is_enabled_debug(message: IncomingMessage) -> bool:
    return message.sender.huid in settings.SMARTLOG_DEBUG_HUIDS


async def smart_logger_middleware(
    message: IncomingMessage, bot: Bot, call_next: IncomingMessageHandlerFunc
) -> None:
    async with wrap_smart_logger(
        log_source="Incoming message",
        context_func=lambda: format_raw_command(message.raw_command),
        debug=is_enabled_debug(message),
    ):
        await call_next(message, bot)
