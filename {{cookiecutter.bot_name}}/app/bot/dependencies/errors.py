"""Module for handling errors and warnings."""

from botx import Message
from loguru import logger

from app.resources import strings


async def internal_error_handler(exc: Exception, message: Message) -> None:
    """Send error message to user and raise error."""

    await message.bot.answer_message(strings.SOMETHING_GOES_WRONG, message)

    logger.exception(exc)

    raise exc
