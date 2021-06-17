"""Dependencies for check that message was send from bot's cts."""
from botx import DependencyFailure, Message

from app.resources import strings


async def message_from_current_cts(message: Message) -> None:
    """Check that user write from bot's cts."""
    if message.is_system_event:
        return

    if not (message.user.ad_domain and message.ad_login):
        await message.bot.answer_message(
            strings.BOT_CANT_COMMUNICATE_WITH_OTHERS_CTS, message
        )
        raise DependencyFailure
