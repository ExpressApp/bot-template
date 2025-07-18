"""Decorators to rethrow and log exceptions."""

import asyncio
import inspect
from functools import wraps
from typing import Any, Callable, Tuple, Type, TypeVar, Union, cast

from app.logger import logger

FunctionType = TypeVar("FunctionType", bound=Callable[..., Any])

CatchExceptionClass = Union[Type[Exception], Tuple[Type[Exception], ...]]
T = TypeVar("T")
Decorator = Callable[[Callable[..., T]], Callable[..., T]]


def _get_error_message(
    ex: Exception,
    func: Callable[..., Any],
    args: tuple[Any, ...] | None = None,
    kwargs: dict[str, Any] | None = None,
    use_short_error_message: bool = True,
) -> str:
    """
    Generate an error message string based on the given exception and function context.

    :param ex: The exception that occurred.
    :param func: The function in which the exception occurred.
    :param args: Optional tuple of positional arguments passed to the function.
    :param kwargs: Optional dictionary of keyword arguments passed to the function.
    :param use_short_error_message: Flag to indicate whether to generate a brief
                                     error message (True) or a detailed one (False).
    :return: A formatted error message string representing the exception and its
             context.
    """

    if use_short_error_message:
        return str(ex)

    error_context = [
        f"Error in function '{func.__module__}.{func.__qualname__}'",
        f"Original exception: {ex.__class__.__name__}: {str(ex)}",
    ]

    filtered_args = args[1:] if args and inspect.ismethod(func) else args

    if filtered_args:
        args_str = ", ".join(str(arg)[:100] for arg in filtered_args)
        error_context.append(f"Args: [{args_str}]")

    if kwargs:
        kwargs_str = ", ".join(f"{k}={str(v)[:100]}" for k, v in kwargs.items())
        error_context.append(f"Kwargs: {kwargs_str}")

    return "\n".join(error_context)


def _create_sync_wrapper(
    func: Callable[..., Any],
    catch_exceptions: CatchExceptionClass,
    raise_exception: Type[Exception],
    use_short_erroro_message: bool,
    log_exception: bool,
) -> Callable[..., Any]:
    """Create a synchronous wrapper function for exception mapping."""

    @wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except catch_exceptions as ex:
            if log_exception:
                logger.error(f"Error in {func.__name__}", exc_info=True)
            error_message = _get_error_message(
                ex, func, args, kwargs, use_short_erroro_message
            )
            raise raise_exception(error_message) from ex

    return sync_wrapper


def _create_async_wrapper(
    func: Callable[..., Any],
    catch_exceptions: CatchExceptionClass,
    raise_exception_class: Type[Exception],
    use_short_error_message: bool,
    log_exception: bool,
) -> Callable[..., Any]:
    """Create an asynchronous wrapper function for exception mapping."""

    @wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except catch_exceptions as ex:
            if log_exception:
                logger.error(f"Error in {func.__name__}", exc_info=True)
            error_message = _get_error_message(
                ex, func, args, kwargs, use_short_error_message
            )
            raise raise_exception_class(error_message) from ex

    return async_wrapper


def exception_mapper(
    raise_exception: Type[Exception],
    catch_exceptions: CatchExceptionClass = Exception,
    use_short_error_message: bool = False,
    log_exception: bool = False,
) -> Decorator:
    """
    Map exceptions from one to another, with optional logging and message adjustments.

    This function creates a decorator to wrap a function or coroutine and modify its
    exception handling behavior. Specifically, it catches specified exceptions and
    raises them as another exception type, with options to log the exception and
    adjust whether a short error message is used.

    :param raise_exception: The exception type to raise instead of the caught exception.
    :param catch_exceptions: The exception type or types to catch within the function.
    :param use_short_error_message: Whether to use a shortened error message when
     raising the new exception.
    :param log_exception: Whether to log the exception when it is caught.
    :return: A decorator for handling exceptions as per the specified parameters.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        if asyncio.iscoroutinefunction(func):
            return cast(
                Callable[..., Any],
                _create_async_wrapper(
                    func,
                    catch_exceptions,
                    raise_exception,
                    use_short_error_message,
                    log_exception,
                ),
            )
        return cast(
            Callable[..., Any],
            _create_sync_wrapper(
                func,
                catch_exceptions,
                raise_exception,
                use_short_error_message,
                log_exception,
            ),
        )

    return decorator
