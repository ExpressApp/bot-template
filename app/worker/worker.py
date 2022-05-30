"""Tasks worker configuration."""

from typing import Any, Dict

from pybotx import Bot
from redis import asyncio as aioredis
from saq import Queue

from app.caching.callback_redis_repo import CallbackRedisRepo
from app.logger import logger

# `saq` import its own settings and hides our module
from app.settings import settings as app_settings

SaqCtx = Dict[str, Any]


async def startup(ctx: SaqCtx) -> None:
    from app.bot.bot import get_bot  # noqa: WPS433

    callback_repo = CallbackRedisRepo(aioredis.from_url(app_settings.REDIS_DSN))
    bot = get_bot(callback_repo, raise_exceptions=False)

    await bot.startup(fetch_tokens=False)

    ctx["bot"] = bot

    logger.info("Worker started")


async def shutdown(ctx: SaqCtx) -> None:
    bot: Bot = ctx["bot"]
    await bot.shutdown()

    logger.info("Worker stopped")


queue = Queue.from_url(app_settings.REDIS_DSN)

settings = {
    "queue": queue,
    "functions": [],
    "cron_jobs": [],
    "concurrency": 8,
    "startup": startup,
    "shutdown": shutdown,
}
