from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

import orjson
from orjson import JSONDecodeError
from pybotx import IncomingMessage
from pydantic import BaseModel, ValidationError

from app.decorators.mapper.exception_mapper import ExceptionMapper
from app.decorators.mapper.factories import EnrichedExceptionFactory
from app.presentation.bot.validators.exceptions import MessageValidationError

T = TypeVar("T", bound=BaseModel)


class IBotRequestParser(ABC, Generic[T]):
    @abstractmethod
    def parse(self, raw_input: Any) -> T:
        """Parse raw input to model."""


class BotXJsonRequestParser(IBotRequestParser[T]):
    def __init__(self, model: type[T]):
        self.model = model

    @ExceptionMapper(
        {
            (JSONDecodeError, ValidationError): EnrichedExceptionFactory(
                MessageValidationError
            )
        },
        is_bound_method=True,
    )
    def parse(self, raw_input: IncomingMessage) -> T:
        message_json = orjson.loads(raw_input.argument)
        return self.model.parse_obj(message_json)


class BotXPlainRequestParser(IBotRequestParser[T]):
    """Base parser which try to create schema from positional arguments.

    Recommended to use strict model object creation with manual kwargs
    """

    def __init__(self, model: type[T]):
        self.model = model

    @ExceptionMapper(
        {ValidationError: EnrichedExceptionFactory(MessageValidationError)},
        is_bound_method=True,
    )
    def parse(self, raw_input: IncomingMessage) -> T:
        if not (message_args := raw_input.argument.strip().split(" ")):
            raise ValidationError("Message is empty", self.model)

        fields = self.model.__fields__.keys()
        message_kwargs = dict(zip(fields, message_args, strict=True))

        return self.model.parse_obj(message_kwargs)
