from unittest.mock import MagicMock

from app.presentation.bot.error_handlers.exceptions_chain_executor import (
    ExceptionHandlersChainExecutor,
)
from tests.unit.error_handlers.test_classes import TestExceptionHandler


async def test_chain_usual_case():
    execution_history = []
    handlers = [
        TestExceptionHandler(index=index, run_history=execution_history)
        for index in range(3)
    ]

    chain_executor = ExceptionHandlersChainExecutor(handlers)

    await chain_executor.execute_chain(MagicMock(), MagicMock(), MagicMock())

    assert execution_history == [0, 1, 2]


async def test_executor_call_only_right_handlers():
    execution_history = []
    handlers = [
        TestExceptionHandler(
            index=index,
            run_history=execution_history,
            should_process_exception=bool(index % 2),
        )
        for index in range(4)
    ]

    chain_executor = ExceptionHandlersChainExecutor(handlers)

    await chain_executor.execute_chain(MagicMock(), MagicMock(), MagicMock())

    assert execution_history == [1, 3]


async def test_executor_deal_with_only_one_handler():
    execution_history = []
    handlers = [
        TestExceptionHandler(
            index=1,
            run_history=execution_history,
        )
    ]

    chain_executor = ExceptionHandlersChainExecutor(handlers)

    await chain_executor.execute_chain(MagicMock(), MagicMock(), MagicMock())

    assert execution_history == [1]


async def test_executor_deal_with_only_one_non_executed_handler():
    history = []
    handlers = [
        TestExceptionHandler(
            index=1, run_history=history, should_process_exception=False
        )
    ]

    chain_executor = ExceptionHandlersChainExecutor(handlers)

    await chain_executor.execute_chain(MagicMock(), MagicMock(), MagicMock())

    assert history == []


async def test_executor_break_the_chain_if_needed():
    execution_history = []
    handlers = [
        TestExceptionHandler(
            index=index, run_history=execution_history, break_the_chain=index >= 1
        )
        for index in range(4)
    ]

    chain_executor = ExceptionHandlersChainExecutor(handlers)

    await chain_executor.execute_chain(MagicMock(), MagicMock(), MagicMock())

    assert execution_history == [
        0,
        1,
    ]
