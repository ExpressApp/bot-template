"""Middlewares to log all requests using smart logger wrapper."""

from pprint import pformat
from typing import Optional, Dict, Any

from pybotx import Bot, IncomingMessage, IncomingMessageHandlerFunc
from pybotx.logger import trim_file_data_in_incoming_json
from pybotx_smart_logger.wrapper import wrap_smart_logger

from app.logger import logger
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


def format_raw_command(raw_command: Optional[Dict[str, Any]]) -> str:
    if raw_command is None:
        logger.warning("Empty `raw_command`")
        return "<empty `raw_command`>"

    trimmed_raw_command = trim_file_data_in_incoming_json(raw_command)
    return pformat(trimmed_raw_command)
