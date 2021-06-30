"""Dependencies for check that message was send from bot's cts."""
from botx import DependencyFailure, Message, SendingMessage

from app.resources import strings


async def message_from_current_cts(message: Message) -> None:
    """Check that user write from bot's cts."""
    if message.is_system_event:
        return

    if not (message.user.ad_domain and message.ad_login):
        answer = SendingMessage.from_message(message=message)
        for bot_credentials in message.bot.bot_accounts:
            if bot_credentials.host == message.user.host:
                answer.text = strings.OTHER_CTS_WITH_BOT_MENTION_WARNING
                answer.mention_contact(bot_credentials.bot_id)
                break

        else:
            answer.text = strings.OTHER_CTS_WARNING

        await message.bot.send(answer)
        raise DependencyFailure
