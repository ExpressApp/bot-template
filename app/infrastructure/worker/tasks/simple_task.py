from typing import Any

from dependency_injector.wiring import inject, Provide
from pybotx import Bot

from app.infrastructure.containers import WorkerStartupContainer

from app.logger import logger


@inject
async def heartbeat_task(
    ctx: dict[str, Any],
    bot: Bot = Provide[WorkerStartupContainer.bot],
):
    # logger.info("Heartbeat task started")

    logger.info(f"Heartbeat task executed {[account.id for account in bot.bot_accounts]}")
