import abc
from abc import ABC

from pybotx import Bot, IncomingMessage
from pydantic import BaseModel

from app.presentation.bot.handlers.error import BaseExceptionHandler
from app.presentation.bot.validators.base import IBotRequestParser


class BaseCommandHandler(ABC):
    def __init__(
        self,
        bot: Bot,
        message: IncomingMessage,
        exception_handler: BaseExceptionHandler | None = None,
    ):
        self._bot = bot
        self._message = message
        self._exception_handler = exception_handler or BaseExceptionHandler()

    @property
    @abc.abstractmethod
    def incoming_argument_parser(
        self,
    ) -> IBotRequestParser | None:
        pass

    @abc.abstractmethod
    async def handle_logic(
        self,
        request_parameter: BaseModel | str | None,
    ) -> None:
        pass

    def get_request_parameter(
        self,
    ) -> BaseModel | str | None:
        return (
            self.incoming_argument_parser.parse(self._message)
            if self.incoming_argument_parser
            else self._message.argument
        )

    async def execute(
        self,
    ) -> None:
        try:
            parameter = self.get_request_parameter()
            await self.handle_logic(parameter)
        except Exception as exc:
            await self._exception_handler.handle_exception(
                exc, self._bot, self._message
            )
