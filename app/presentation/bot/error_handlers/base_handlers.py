from abc import ABC, abstractmethod
from typing import Self, Callable
from uuid import UUID

from pybotx import Bot, IncomingMessage, BotShuttingDownError

from app.logger import logger
from app.presentation.bot.resources import strings


class AbstractExceptionHandler(ABC):
    def __init__(
        self,
        next_handler: Self | None = None,
        stop_on_failure: bool = False,
        break_the_chain: bool = False,
    ):
        self._next_handler = next_handler
        self._stop_on_failure = stop_on_failure
        self._break_the_chain = break_the_chain

    @abstractmethod
    def should_process_exception(
        self, exc: Exception, bot: Bot, message: IncomingMessage
    ) -> bool:
        pass

    @abstractmethod
    async def process_exception(
        self,
        exc: Exception,
        bot: Bot,
        message: IncomingMessage,
        exception_id: UUID | None,
    ):
        pass

    async def handle_exception(
        self,
        exc: Exception,
        bot: Bot,
        message: IncomingMessage,
        exception_id: UUID | None = None,
    ) -> None:
        if self.should_process_exception(exc, bot, message):
            try:
                await self.process_exception(exc, bot, message, exception_id)
                if self._next_handler and not self._break_the_chain:
                    await self._next_handler.handle_exception(
                        exc, bot, message, exception_id
                    )
            except Exception as exc:
                logger.error(
                    f"Error handling exception {exception_id}: {exc}", exc_info=True
                )
                if self._stop_on_failure:
                    return
                if self._next_handler:
                    await self._next_handler.process_exception(exc, bot, message)


class LoggingExceptionHandler(AbstractExceptionHandler):
    def should_process_exception(
        self, exc: Exception, bot: Bot, message: IncomingMessage
    ) -> bool:
        return True

    def process_exception(
        self,
        exc: Exception,
        bot: Bot,
        message: IncomingMessage,
        exception_id: UUID | None,
    ) -> None:
        logger.error(f"Error {exception_id}:{exc}", exc_info=exc)


class DropFSMOnErrorHandler(AbstractExceptionHandler):
    def should_process_exception(
        self, exc: Exception, bot: Bot, message: IncomingMessage
    ) -> bool:
        return True

    async def process_exception(
        self, exc: Exception, bot: Bot, message: IncomingMessage, exception_id: UUID
    ) -> None:
        if fsm_manager := getattr(message.state, "fsm", None):
            await fsm_manager.drop_state()


class SendErrorExplainToUserHandler(AbstractExceptionHandler):
    def __init__(
        self,
        next_handler: Self | None = None,
        exception_explain_mapping: dict[type[Exception], str | Callable] | None = None,
    ):
        super().__init__(next_handler)
        self.exception_explain_mapping = exception_explain_mapping or {}

    def should_process_exception(
        self, exc: Exception, bot: Bot, message: IncomingMessage
    ) -> bool:
        return True

    async def _get_exception_message_for_user(
        self,
        exc: Exception,
        bot: Bot,
        message: IncomingMessage,
        exception_id: UUID | None = None,
    ) -> str:
        if explanation := self.exception_explain_mapping.get(type(exc)) is not None:
            if isinstance(explanation, str):
                raw_explanation = explanation
            else:
                raw_explanation = explanation(exc, bot, message, exception_id)

            return f"{raw_explanation}. Идентификатор ошибки:{exception_id}"

        return strings.SOMETHING_GOES_WRONG.format(error_uuid=exception_id)

    async def process_exception(
        self,
        exc: Exception,
        bot: Bot,
        message: IncomingMessage,
        exception_id: UUID | None,
    ) -> None:
        message_text = await self._get_exception_message_for_user(exc, bot, message)
        await bot.answer_message(
            message_text,
            wait_callback=not isinstance(exc, BotShuttingDownError),
        )
