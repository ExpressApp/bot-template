import time
from typing import Callable

import pytest


@pytest.fixture(scope="session")
def printer(request) -> Callable:  # pragma: no cover
    """
    Print progress steps in verbose mode.

    Create public function `printer` for usage in any test helpers, not only fixtures.
    Based on: https://github.com/pytest-dev/pytest-print/blob/master/src/pytest_print/__init__.py
    """

    def no_op(*_) -> None:
        """Do nothing."""

    if request.config.getoption("verbose") <= 0:
        return no_op

    terminal_reporter = request.config.pluginmanager.getplugin("terminalreporter")
    capture_manager = request.config.pluginmanager.get_plugin("capturemanager")
    if terminal_reporter is None:
        return no_op  # pragma: no cover

    first_call = True
    start_time = time.monotonic()

    def _print(msg: str) -> None:
        """Print messages with time duration."""
        new_line = ""
        nonlocal first_call
        if first_call:  # in case of the first call we don't have a new empty line
            new_line = "\n"
            first_call = False
        delta = time.monotonic() - start_time
        log_line = f"{new_line}{delta:.3f}s :: {msg}\n"
        with capture_manager.global_and_fixture_disabled():
            terminal_reporter.write(log_line)

    return _print
