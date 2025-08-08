from abc import ABCMeta
from uuid import uuid4

from pybotx import Bot, IncomingMessage

from app.presentation.bot.error_handlers.base_handlers import (
    AbstractExceptionHandler,
    DropFSMOnErrorHandler,
    LoggingExceptionHandler,
    SendErrorExplainToUserHandler,
)

HandlerOrHandlerClass = (
    AbstractExceptionHandler | type[AbstractExceptionHandler] | ABCMeta
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
        self,
        handlers: list[HandlerOrHandlerClass] | None = None,
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
        self,
        handler: HandlerOrHandlerClass,
    ) -> AbstractExceptionHandler:
        return handler if isinstance(handler, AbstractExceptionHandler) else handler()

    def _create_chain(
        self,
        handlers: list[HandlerOrHandlerClass] | None = None,
    ) -> tuple[AbstractExceptionHandler | None, AbstractExceptionHandler | None]:
        """
        Create a linked list of exception handlers from the given list.

        This method takes a sequence of exception handler classes or instances
        and chains them together into a linked list. The returned tuple contains
        the head and tail of the constructed chain.

        warning:
           This method modifies the passed objects of
           class:`AbstractExceptionHandler` type in place.
        """
        if not handlers:
            return None, None

        head_handler = self._get_handler(handlers[0])

        tail_handler = head_handler
        for handler in handlers[1:]:
            new_tail_handler = self._get_handler(handler)
            tail_handler.next_handler = new_tail_handler
            tail_handler = new_tail_handler
        return head_handler, tail_handler

    def extend(self, handlers: list[HandlerOrHandlerClass] | None) -> None:
        """Append handlers to the chain"""
        if not handlers:
            return

        new_head, new_tail = self._create_chain(handlers)
        if self._is_empty():
            self._chain_head = new_head
        else:
            # The tail and head cannot be None at the same time.
            self._chain_tail.next_handler = new_head  # type: ignore

        self._chain_tail = new_tail

    def append(self, handler: HandlerOrHandlerClass) -> None:
        """Append handler to the end of a chain"""
        new_tail = self._get_handler(handler)

        if self._is_empty():
            self._chain_head = new_tail
            self._chain_tail = new_tail
        else:
            self._chain_tail.next_handler = new_tail  # type:ignore

    def _is_empty(self) -> bool:
        return self._chain_head is None and self._chain_tail is None


DEFAULT_HANDLERS: list[HandlerOrHandlerClass] = [
    LoggingExceptionHandler,
    DropFSMOnErrorHandler,
]

DEFAULT_HANDLERS_WITH_EXPLAIN: list[HandlerOrHandlerClass] = DEFAULT_HANDLERS + [
    SendErrorExplainToUserHandler
]
