from abc import ABC, abstractmethod
from typing import Any

from app.decorators.mapper.context import ExceptionContext


class ContextAwareError(Exception):
    def __init__(
        self, message: str, context: ExceptionContext | None = None, *args: Any
    ):
        super().__init__(message, *args)
        self.context = context

    def __str__(self) -> str:
        base = super().__str__()
        if self.context:
            return f"{base} | context={self.context.formatted_context}"
        return base


class ExceptionFactory(ABC):
    """
    Create and describe a factory for exceptions.

    This class is an abstract base class meant to define the interface for an
    exception factory.

    """

    @abstractmethod
    def make_exception(self, context: ExceptionContext) -> Exception:
        """Make an exception based on the given context."""


class PassThroughExceptionFactory(ExceptionFactory):
    """Factory for exceptions that should be passed through without create a new one.

    Useful for cases when broad Exception cached and wrapped to a common Exception type.
    """

    def make_exception(self, context: ExceptionContext) -> Exception:
        return context.original_exception


class EnrichedExceptionFactory(ExceptionFactory):
    """
    Create and manage enriched exceptions based on a given exception type.

    This class provides a mechanism to create exceptions dynamically,
    enriching them with a formatted context.

    :ivar generated_error: The type of exception to generate when creating
                           an enriched exception.
    :type generated_error: type[ContextAwareError]
    """

    def __init__(self, generated_error: type[ContextAwareError]):
        self.generated_error = generated_error

    def make_exception(self, context: ExceptionContext) -> ContextAwareError:
        return self.generated_error(str(context.original_exception), context=context)
