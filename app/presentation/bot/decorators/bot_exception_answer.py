"""Module for translation Exception errors to user friendly messages."""

import functools
import logging
from typing import Any, Callable

from pybotx import Bot

logger = logging.getLogger(__name__)


def _get_user_message(
    exception_map: dict[type[Exception], str | Callable], exc: Exception
) -> str | None:
    """Extract user message from exception mapping."""
    exception_message_to_user = exception_map.get(type(exc))
    if callable(exception_message_to_user):
        return exception_message_to_user(exc)
    return exception_message_to_user


def explain_exception_to_user(
    mapping: dict[type[Exception], str | Callable[[Exception], str]],
) -> Callable:
    """
    Decorate a function to catch specified exceptions and send a response to the user.

    For each caught exception, it responds using either a string message or a callable
     response provided in the `exception_map`.

    :param mapping: A dictionary mapping exception types to either string messages
        or callables that construct a response when invoked with the exception as an
        argument. The keys must be subclasses of `Exception`, and the values must be
        either strings or callables.
    """

    def decorator(func: Callable) -> Callable:  # type: ignore
        @functools.wraps(func)
        async def wrapper(bot: Bot, *args, **kwargs) -> Any:  # type: ignore
            try:
                return await func(
                    bot,
                    *args,
                    **kwargs,
                )
            except tuple(mapping.keys()) as exc:
                if (message := _get_user_message(mapping, exc)) is not None:
                    await bot.answer_message(message)
                raise

        return wrapper

    return decorator
