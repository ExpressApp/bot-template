"""Handler to work with unexpected errors."""

from pybotx import Bot, BotShuttingDownError, IncomingMessage

from app.logger import logger
from app.resources import strings


async def internal_error_handler(
    message: IncomingMessage, bot: Bot, exc: Exception
) -> None:
    logger.exception("Internal error:")

    is_bot_active = not isinstance(exc, BotShuttingDownError)
    await bot.answer_message(
        strings.SOMETHING_GOES_WRONG,
        # We can't receive callback when bot is shutting down
        wait_callback=is_bot_active,
    )
