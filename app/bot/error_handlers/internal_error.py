"""Handler to work with unexpected errors."""
from uuid import uuid4

from pybotx import Bot, BotShuttingDownError, IncomingMessage

from app.logger import logger
from app.resources import strings


async def internal_error_handler(
    message: IncomingMessage, bot: Bot, exc: Exception
) -> None:
    error_uuid = uuid4()
    logger.exception(f"Internal error {error_uuid}:")

    fsm_manager = getattr(message.state, "fsm", None)
    if fsm_manager:
        await fsm_manager.drop_state()

    is_bot_active = not isinstance(exc, BotShuttingDownError)
    await bot.answer_message(
        strings.SOMETHING_GOES_WRONG.format(error_uuid=error_uuid),
        # We can't receive callback when bot is shutting down
        wait_callback=is_bot_active,
    )
