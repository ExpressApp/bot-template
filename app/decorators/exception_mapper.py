"""Decorators to rethrow and log exceptions."""

from abc import ABC, abstractmethod
from functools import cached_property, wraps
from inspect import iscoroutinefunction
from typing import Any, Callable, Type

from cachetools import LRUCache  # type:ignore

from app.logger import logger


class ExceptionContext:
    SENSITIVE_KEYS: frozenset[str] = frozenset(
        ("password", "token", "key", "secret", "auth", "credential", "passwd")
    )

    def __init__(
        self,
        original_exception: Exception,
        func: Callable,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ):
        self.original_exception = original_exception
        self.func = func
        self.args = args
        self.kwargs = kwargs

    @cached_property
    def formatted_context(self) -> str:
        error_context = [
            f"Error in function '{self.func.__module__}.{self.func.__qualname__}'"
        ]

        if self.args:
            args_str = ", ".join(self._sanitised_value(arg) for arg in self.args)
            error_context.append(f"Args: [{args_str}]")

        if self.kwargs:
            kwargs_str = ", ".join(
                f"{k}={self._sanitised_value(v, k)}" for k, v in self.kwargs.items()
            )
            error_context.append(f"Kwargs: {kwargs_str}")

        return "\n".join(error_context).replace("{", "{{").replace("}", "}}")

    def _sanitised_value(
        self,
        value: Any,
        key: str | None = None,
    ) -> str:
        if key is not None and key.lower() in self.SENSITIVE_KEYS:
            return "****HIDDEN****"

        try:
            str_value = str(value)
            return f"{str_value[:100]}..." if len(str_value) > 100 else str_value
        except Exception:
            return f"<{type(value).__name__} object - str() failed>"


class ExceptionFactory(ABC):
    """
    Create and describe a factory for exceptions.

    This class is an abstract base class meant to define the interface for an
    exception factory.

    """

    @abstractmethod
    def make_exception(self, context: ExceptionContext) -> Exception:
        """Make an exception based on the given context."""


class EnrichedExceptionFactory(ExceptionFactory):
    """
    Create and manage enriched exceptions based on a given exception type.

    This class provides a mechanism to create exceptions dynamically,
    enriching them with a formatted context. It extends the behavior of
    the base ExceptionFactory class by incorporating the concept of a
    generated error type and formatted context.

    :ivar generated_error: The type of exception to generate when creating
                           an enriched exception.
    :type generated_error: type[Exception]
    """

    def __init__(self, generated_error: type[Exception]):
        self.generated_error = generated_error

    def make_exception(self, context: ExceptionContext) -> Exception:
        return self.generated_error(context.formatted_context)


ExceptionOrTupleOfExceptions = Type[Exception] | tuple[Type[Exception], ...]


class ExceptionMapper:
    """Exception-mapping decorator with bounded LRU caching and dynamic MRO lookup."""

    def __init__(
        self,
        exception_map: dict[ExceptionOrTupleOfExceptions, ExceptionFactory],
        max_cache_size: int = 512,
        log_error: bool = True,
        is_bound_method: bool = False,
    ):
        self.mapping = self._get_flat_map(exception_map)
        self.exception_catchall_factory = self.mapping.pop(Exception, None)
        self._lru_cache: LRUCache = LRUCache(maxsize=max_cache_size)
        self.log_error = log_error
        self.is_bound_method = is_bound_method

    def __call__(self, func: Callable) -> Callable:
        return (
            self._async_wrapper(func)
            if iscoroutinefunction(func)
            else self._sync_wrapper(func)
        )

    def _get_flat_map(
        self,
        exception_map: dict[ExceptionOrTupleOfExceptions, ExceptionFactory],
    ) -> dict[Type[Exception], ExceptionFactory]:
        flat_map: dict[Type[Exception], ExceptionFactory] = {}
        for exception_class, factory in exception_map.items():
            if isinstance(exception_class, tuple):
                for exc_type in exception_class:
                    flat_map[exc_type] = factory
            else:
                flat_map[exception_class] = factory
        return flat_map

    def _async_wrapper(self, func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception as exc:
                self._handle_exception_logic(exc, func, args, kwargs)

        return wrapper

    def _sync_wrapper(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                self._handle_exception_logic(exc, func, args, kwargs)

        return wrapper

    def _filtered_args(self, args: tuple[Any, ...]) -> tuple[Any, ...]:
        return args[1:] if args and self.is_bound_method else args

    def _handle_exception_logic(
        self,
        exc: Exception,
        func: Callable,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> None:
        context = ExceptionContext(exc, func, self._filtered_args(args), kwargs)
        if self.log_error:
            logger.error(context.formatted_context, exc_info=True)

        if exception_factory := self._get_exception_factory(type(exc)):
            raise exception_factory.make_exception(context) from exc

        raise exc

    def _get_exception_factory(
        self, exc_type: Type[Exception]
    ) -> ExceptionFactory | None:
        # Try to get from_cache
        if cached_factory := self._lru_cache.get(exc_type):
            return cached_factory

        # Try to find exception parents in base mapping and put to cache if found
        for exc_class in exc_type.mro():
            if target_exception_factory := self.mapping.get(exc_class):  # type:ignore
                self._lru_cache[exc_type] = target_exception_factory
                return target_exception_factory

        # exception is not presented in base mapping, but Exception in base mapping
        if self.exception_catchall_factory:
            self._lru_cache[exc_type] = self.exception_catchall_factory
            return self.exception_catchall_factory

        return None
