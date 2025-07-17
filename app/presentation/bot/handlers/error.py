from typing import Callable
from uuid import uuid4

from pybotx import Bot, IncomingMessage, BotShuttingDownError

from app.logger import logger
from app.presentation.bot.validators.exceptions import MessageValidationError
from app.presentation.bot.resources import strings


class BaseExceptionHandler:
    def __init__(
        self,
        exception_explain_mapping: dict[type[Exception], str | Callable] | None = None,
    ):
        self.exception_explain_mapping = exception_explain_mapping or {}

    async def handle_exception(
        self, exc: Exception, bot: Bot, message: IncomingMessage
    ) -> None:
        if fsm_manager := getattr(message.state, "fsm", None):
            await fsm_manager.drop_state()

        user_answer = await self._get_exception_message_for_user(
            exc,
        )

        logger.error(f"Error: {user_answer}", exc_info=exc)

        await bot.answer_message(
            user_answer,
            wait_callback=not isinstance(exc, BotShuttingDownError),
        )

    async def _get_exception_message_for_user(self, exc: Exception) -> str:
        error_uuid = uuid4()

        if explanation := self.exception_explain_mapping.get(type(exc)):
            if isinstance(explanation, str):
                raw_message = explanation
            else:
                raw_message = explanation(exc)

            return f"{raw_message}. Идентификатор ошибки:{error_uuid}"
        elif isinstance(exc, MessageValidationError):
            return f"Ошибка валидации запроса: {exc}. Идентификатор ошибки:{error_uuid}"
        else:
            return strings.SOMETHING_GOES_WRONG.format(error_uuid=error_uuid)
