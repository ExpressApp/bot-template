from abc import ABC, abstractmethod
from typing import Callable, Self
from uuid import UUID

from pybotx import Bot, BotShuttingDownError, IncomingMessage

from app.decorators.mapper.factories import ContextAwareError
from app.logger import logger
from app.presentation.bot.resources import strings


class AbstractExceptionHandler(ABC):
    """Abstract template class for exception handlers."""

    def __init__(
        self,
        next_handler: Self | None = None,
        stop_on_failure: bool = False,
        break_the_chain: bool = False,
    ):
        """Constructor for exception handler.

        Args:
             next_handler: The next handler in the chain.
             stop_on_failure: Whether to stop processing the chain on this
                handler failure.
             break_the_chain: Whether to break the chain if this handler processed
                the exception successfully.

        """
        self.next_handler = next_handler
        self._stop_on_failure = stop_on_failure
        self._break_the_chain = break_the_chain

    @abstractmethod
    def should_process_exception(
        self, exc: Exception, bot: Bot, message: IncomingMessage
    ) -> bool:
        """Method to determine whether exception should be processed or not."""
        pass

    @abstractmethod
    async def process_exception(
        self,
        exc: Exception,
        bot: Bot,
        message: IncomingMessage,
        exception_id: UUID | None,
    ) -> None:
        """Method to process exception."""
        pass

    async def handle_exception(
        self,
        exc: Exception,
        bot: Bot,
        message: IncomingMessage,
        exception_id: UUID | None = None,
    ) -> None:
        """Base method to handle exception.
        Execute main chain logic"""
        if self.should_process_exception(exc, bot, message):
            try:
                await self.process_exception(exc, bot, message, exception_id)

                if self.next_handler and not self._break_the_chain:
                    await self.next_handler.handle_exception(
                        exc, bot, message, exception_id
                    )
            except Exception as exc:
                logger.error(
                    f"Error handling exception {exception_id}",
                    exc_info=True,
                )
                if self._stop_on_failure:
                    return
                if self.next_handler:
                    await self.next_handler.process_exception(
                        exc, bot, message, exception_id
                    )
        else:
            if self.next_handler:
                await self.next_handler.handle_exception(
                    exc, bot, message, exception_id
                )


class LoggingExceptionHandler(AbstractExceptionHandler):
    def should_process_exception(
        self, exc: Exception, bot: Bot, message: IncomingMessage
    ) -> bool:
        return True

    async def process_exception(
        self,
        exc: Exception,
        bot: Bot,
        message: IncomingMessage,
        exception_id: UUID | None,
    ) -> None:
        # TODO: add structured context logging
        if isinstance(exc, ContextAwareError) and exc.context is not None:
            msg = f"Error {exception_id}:{exc}. Context:{exc.context.formatted_context}"
        else:
            msg = f"Error {exception_id}:{exc}"

        logger.error(msg, exc_info=exc)


class DropFSMOnErrorHandler(AbstractExceptionHandler):
    def should_process_exception(
        self, exc: Exception, bot: Bot, message: IncomingMessage
    ) -> bool:
        return True

    async def process_exception(
        self,
        exc: Exception,
        bot: Bot,
        message: IncomingMessage,
        exception_id: UUID | None,
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
        if (explanation := self.exception_explain_mapping.get(type(exc))) is not None:
            if isinstance(explanation, str):
                raw_explanation = explanation
            else:
                raw_explanation = explanation(exc, bot, message, exception_id)

            return strings.SAMPLE_RECORD_BAD_DATA_FORMAT.format(
                explanation=raw_explanation, exception_id=exception_id
            )

        return strings.SOMETHING_GOES_WRONG.format(error_uuid=exception_id)

    async def process_exception(
        self,
        exc: Exception,
        bot: Bot,
        message: IncomingMessage,
        exception_id: UUID | None,
    ) -> None:
        message_text = await self._get_exception_message_for_user(
            exc, bot, message, exception_id
        )
        await bot.answer_message(
            message_text,
            wait_callback=not isinstance(exc, BotShuttingDownError),
        )
