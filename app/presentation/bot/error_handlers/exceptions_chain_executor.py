from uuid import uuid4

from pybotx import Bot, IncomingMessage

from app.presentation.bot.error_handlers.base_handlers import (
    AbstractExceptionHandler,
    SendErrorExplainToUserHandler,
    LoggingExceptionHandler,
    DropFSMOnErrorHandler,
)


class ExceptionHandlersChainExecutor:
    """
    Executes a chain of exception handlers in sequence.

    This class manages the execution chain of exception handlers, allowing for the
    construction, extension, and execution of a linked chain. The purpose is to
    process exceptions by passing them through a series of handlers where each
    handler may handle or propagate the exception down the chain. Handlers can be
    defined as either instances or types of `AbstractExceptionHandler`.


    """

    def __init__(
        self, handlers: list[type[AbstractExceptionHandler] | AbstractExceptionHandler]
    ):
        self._chain_head, self._chain_tail = self._create_chain(handlers)

    async def execute_chain(
        self, exc: Exception, bot: Bot, message: IncomingMessage
    ) -> None:
        """
        Handles the execution of an exception handling chain.

        This method initiates a chain of exception handling by starting with
        the head of the chain if it exists. Each node in the chain processes
        the exception and potentially passes it along for further handling.
        The chain makes use of a unique exception identifier for tracking.

        Parameters:
            exc (Exception): The exception instance to be handled.
            bot (Bot): The bot context required for processing the exception.
            message (IncomingMessage): The incoming message context related
                to the exception.
        """
        if self._chain_head is None:
            return

        exception_id = uuid4()
        await self._chain_head.handle_exception(exc, bot, message, exception_id)

    def _get_handler(
        self, handler: AbstractExceptionHandler | type[AbstractExceptionHandler]
    ) -> AbstractExceptionHandler:
        return handler if isinstance(handler, AbstractExceptionHandler) else handler()

    def _create_chain(
        self, handlers: list[type[AbstractExceptionHandler] | AbstractExceptionHandler]
    ) -> tuple[AbstractExceptionHandler | None, AbstractExceptionHandler | None]:
        if not handlers:
            return None, None

        first_handler = self._get_handler(handlers[0])

        last_handler = first_handler
        for handler in handlers[1:]:
            next_handler = self._get_handler(handler)
            last_handler.next_handler = next_handler
            last_handler = next_handler
        return first_handler, last_handler

    def extend(
        self, handlers: list[AbstractExceptionHandler | type[AbstractExceptionHandler]]
    ):
        """Append handlers to the chain"""
        new_head, new_tail = self._create_chain(handlers)
        if self._chain_head is None:
            self._chain_head = new_head
        else:
            self._chain_tail.next_handler = new_head

        self._chain_tail = new_tail

    def append(
        self, handler: AbstractExceptionHandler | type[AbstractExceptionHandler]
    ):
        """Append handler to the end of chain"""
        new_tail = self._get_handler(handler)
        self._chain_tail.next_handler = new_tail


DEFAULT_HANDLERS = [
    LoggingExceptionHandler,
    DropFSMOnErrorHandler,
]
DEFAULT_EXCEPTION_HANDLER_EXECUTOR = ExceptionHandlersChainExecutor(DEFAULT_HANDLERS)

DEFAULT_HANDLERS_WITH_EXPLAIN = DEFAULT_HANDLERS + [SendErrorExplainToUserHandler]

DEFAULT_EXCEPTION_HANDLER_EXECUTOR_WITH_EXPLAIN = ExceptionHandlersChainExecutor(
    handlers=DEFAULT_HANDLERS_WITH_EXPLAIN
)
