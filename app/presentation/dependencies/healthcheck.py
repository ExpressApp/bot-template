"""Bot dependency for healthcheck."""

from asyncio.exceptions import TimeoutError
from typing import Optional

from fastapi import Depends, Request
from pybotx import Bot
from sqlalchemy.sql import text

from app.infrastructure.worker.worker import queue
from app.settings import settings


async def check_db_connection(request: Request) -> Optional[str]:
    assert isinstance(request.app.state.bot, Bot)

    bot = request.app.state.bot
    session_factory = bot.state.db_session_factory

    async with session_factory() as db_session:
        try:
            await db_session.execute(text("SELECT 1"))
        except Exception as exc:
            return str(exc)

    return None


check_db_connection_dependency = Depends(check_db_connection)


async def check_redis_connection(request: Request) -> Optional[str]:
    assert isinstance(request.app.state.bot, Bot)

    bot = request.app.state.bot
    return await bot.state.redis_repo.ping()


check_redis_connection_dependency = Depends(check_redis_connection)


async def check_worker_status() -> Optional[str]:
    job = await queue.enqueue("healthcheck")

    if not job:
        return None

    try:
        await job.refresh(settings.WORKER_TIMEOUT_SEC)
    except TimeoutError:
        return "Worker is overloaded or not launched"
    except Exception as exc:
        return str(exc)

    return None


check_worker_status_dependency = Depends(check_worker_status)
