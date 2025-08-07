"""Tasks worker configuration."""

from typing import Any, Dict

from dependency_injector.wiring import Provide, inject
from pybotx import Bot
from redis.asyncio import Redis
from saq import CronJob, Queue

from app.infrastructure.containers import WorkerStartupContainer, BaseStartupContainer
from app.infrastructure.worker.tasks.simple_task import heartbeat_task
from app.logger import logger
from app.settings import settings

SaqCtx = Dict[str, Any]


# queue = Queue(aioredis.from_url(settings.REDIS_DSN), name="bot_template")
queue = Queue.from_url(settings.REDIS_DSN, name="bot_template_worker")


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
    worker_startup_container = BaseStartupContainer()

    worker_startup_container.wire(modules=[__name__, "app.infrastructure.worker.tasks"])
    await _startup_with_injection()

    logger.info("Worker started")


async def shutdown(ctx: SaqCtx) -> None:
    await _shutdown_with_injection()
    logger.info("Worker stopped")


saq_settings = {
    "queue": queue,
    "functions": [],
    "cron_jobs": [
        CronJob(
            function=heartbeat_task,
            cron="* * * * * */5",
            unique=False,
            timeout=15,
        ),
    ],
    "concurrency": settings.WORKER_CONCURRENCY,
    "startup": startup,
    "shutdown": shutdown,
}
