from functools import cached_property
from typing import Any, Callable


class ExceptionContext:
    """Class to get exception rising context."""

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
        """Format exception context for logging."""
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
        """Exclude sensitive data from logging

        TODO: add deeper sanitation for nested structures
        """
        if key is not None and key.lower() in self.SENSITIVE_KEYS:
            return "****HIDDEN****"

        try:
            str_value = str(value)
            return f"{str_value[:100]}..." if len(str_value) > 100 else str_value
        except Exception:
            return f"<{type(value).__name__} object - str() failed>"
