"""Decorators to rethrow and log exceptions."""

from functools import wraps
from inspect import iscoroutinefunction
from typing import Any, Callable, Type

from cachetools import LRUCache  # type:ignore

from app.decorators.mapper.context import ExceptionContext
from app.decorators.mapper.factories import ExceptionFactory

ExceptionOrTupleOfExceptions = Type[Exception] | tuple[Type[Exception], ...]


class ExceptionMapper:
    """Exception-mapping decorator with bounded LRU caching and dynamic MRO lookup.

    The main decorator purpose is map exception between application layers and enrich
        exceptions by context.
    """

    def __init__(
        self,
        exception_map: dict[ExceptionOrTupleOfExceptions, ExceptionFactory],
        max_cache_size: int = 512,
        is_bound_method: bool = False,
    ):
        self.mapping = self._get_exceptions_flat_map(exception_map)
        self.exception_catchall_factory = self.mapping.pop(Exception, None)
        self._lru_cache: LRUCache = LRUCache(maxsize=max_cache_size)
        self.is_bound_method = is_bound_method

    def __call__(self, func: Callable) -> Callable:
        return (
            self._async_wrapper(func)
            if iscoroutinefunction(func)
            else self._sync_wrapper(func)
        )

    def _get_exceptions_flat_map(
        self,
        exception_map: dict[ExceptionOrTupleOfExceptions, ExceptionFactory],
    ) -> dict[Type[Exception], ExceptionFactory]:
        """Do a flat map from given exception map."""
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
        if exception_factory := self._get_exception_factory(type(exc)):
            context = ExceptionContext(exc, func, self._filtered_args(args), kwargs)
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

        # exception is not presented in base mapping, but catchall is presented
        if self.exception_catchall_factory:
            self._lru_cache[exc_type] = self.exception_catchall_factory
            return self.exception_catchall_factory

        return None
