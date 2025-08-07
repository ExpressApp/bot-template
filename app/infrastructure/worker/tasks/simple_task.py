import asyncio
from typing import Any

from dependency_injector.wiring import Provide, inject
from pybotx import Bot

from app.infrastructure.containers import WorkerStartupContainer
from app.logger import logger


@inject
async def heartbeat_task(
    ctx: dict[str, Any],
    bot: Bot = Provide[WorkerStartupContainer.bot],
) -> None:
    """Simple example of a periodic task"""
    task_name = asyncio.current_task().get_name()  # type:ignore
    logger.info(f"Task {task_name} Heartbeat task executed start bot id {id(bot)}")
    await asyncio.sleep(10)
    logger.info(f"Task {task_name} Heartbeat task executed end bot id {id(bot)}")
