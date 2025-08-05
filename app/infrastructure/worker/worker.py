"""Tasks worker configuration."""

from typing import Any, Dict, Literal

from dependency_injector.wiring import inject, Provide
from pybotx import Bot
from redis import asyncio as aioredis
from redis.asyncio import Redis
from saq import Queue, CronJob

from app.infrastructure.containers import WorkerStartupContainer
from app.infrastructure.repositories.caching.callback_redis_repo import (
    CallbackRedisRepo,
)
from app.infrastructure.worker.tasks.simple_task import heartbeat_task
from app.logger import logger

# `saq` import its own settings and hides our module
from app.settings import settings as app_settings

SaqCtx = Dict[str, Any]



queue = Queue(aioredis.from_url(app_settings.REDIS_DSN), name="bot_refactor")

@inject
async def _startup_with_injection(
    bot: Bot = Provide[WorkerStartupContainer.bot],
) -> None:
    """Helper function for starting bot with dependencies injection."""
    await bot.startup(fetch_tokens=False)


@inject
async def _shutdown_with_injection(
    bot: Bot = Provide[WorkerStartupContainer.bot],
    redis_client: Redis = Provide[WorkerStartupContainer.redis_client],
) -> None:
    """Helper function for shutting down bot with dependencies injection."""
    await bot.shutdown()
    await redis_client.aclose()


async def startup(ctx: SaqCtx) -> None:
    worker_startup_container = WorkerStartupContainer()

    queue.add_cron_job(
        CronJob(function=heartbeat_task, cron="*/5 * * * * *", unique=True)
    )
    worker_startup_container.wire(modules=[__name__, "app.infrastructure.worker.tasks"])

    await _startup_with_injection()

    logger.info("Worker started")


async def shutdown(ctx: SaqCtx) -> None:
    await _shutdown_with_injection()
    logger.info("Worker stopped")


settings = {
    "queue": queue,
    "functions": [],
    # "cron_jobs": [
    #     CronJob(
    #         function=heartbeat_task,
    #         cron="*/5 * * * * *",
    #         unique=True,
    #         # timeout=app_settings.PERIODIC_TASKS_DEFAULT_TIMEOUT,
    #         # heartbeat=app_settings.PERIODIC_TASKS_DEFAULT_HEARTBEAT,
    #         # retries=app_settings.PERIODIC_TASKS_DEFAULT_RETRIES,
    #         # ttl=app_settings.PERIODIC_TASKS_DEFAULT_TTL,
    #     ),
    # ],
    "concurrency": 8,
    "startup": startup,
    "shutdown": shutdown,
}
