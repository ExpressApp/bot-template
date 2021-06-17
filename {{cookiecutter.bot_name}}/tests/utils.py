import time
from functools import wraps
from os import environ
from typing import Any, Callable, Type


def do_with_retry(
    exc_to_catch: Type[Exception], reraised_exc: Type[Exception], error_msg: str
) -> Callable:
    def outer_wrapper(call: Callable) -> Callable:
        @wraps(call)
        def inner_wrapper(*args: Any, printer: Callable, **kwargs: Any) -> Any:
            start_time = time.monotonic()
            last_time = time.monotonic()
            retry_timeout = int(environ.get("RETRY_TIMEOUT", 25))
            while last_time - start_time < retry_timeout:
                try:
                    return call(*args, printer=printer, **kwargs)
                except exc_to_catch:  # pragma: no cover
                    time.sleep(2)
                    last_time = time.monotonic()
                    printer(f"retry {last_time - start_time:.3f}s < {retry_timeout}s")
            else:
                raise reraised_exc(error_msg)  # pragma: no cover

        return inner_wrapper

    return outer_wrapper
