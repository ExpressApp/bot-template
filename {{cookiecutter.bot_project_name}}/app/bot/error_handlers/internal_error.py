"""Handler to work with unexpected errors."""

from botx import Bot, BotShuttingDownError, IncomingMessage

from app.logger import logger
from app.resources import strings


async def internal_error_handler(
    message: IncomingMessage, bot: Bot, exc: Exception
) -> None:
    logger.exception("Internal error:")

    await bot.answer_message(
        strings.SOMETHING_GOES_WRONG,
        # We can't receive callback when bot is shutting down
        wait_callback=isinstance(exc, BotShuttingDownError),
    )
