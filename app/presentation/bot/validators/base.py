from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Any

from orjson import orjson, JSONDecodeError
from pybotx import IncomingMessage
from pydantic import BaseModel, ValidationError

from app.presentation.bot.validators.exceptions import MessageValidationError

T = TypeVar("T", bound=BaseModel)


class IBotRequestParser(ABC, Generic[T]):
    @abstractmethod
    def parse(self, raw_input: Any) -> T:
        """Parse raw input to model."""


class BotXJsonRequestParser(IBotRequestParser[T]):
    def __init__(self, model: type[T]):
        self.model = model

    def parse(self, raw_input: IncomingMessage) -> T:
        try:
            message_json = orjson.loads(raw_input.argument)
            return self.model.parse_obj(message_json)
        except JSONDecodeError as ex:
            raise MessageValidationError(str(ex)) from ex
        except ValidationError as ex:
            raise MessageValidationError(
                ",".join(error["msg"] for error in ex.errors())
            ) from ex
