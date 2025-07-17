from fastapi import Request
from sqlalchemy.sql import text
from asyncio.exceptions import TimeoutError
from pybotx import Bot

from app.application.service.interfaces import HealthCheckService
from app.infrastructure.worker.worker import queue
from app.settings import settings


class PostgresHealthCheck(HealthCheckService):
    def __init__(self, request: Request):
        self._request = request

    async def check(self):
        bot: Bot = self._request.app.state.bot
        session_factory = bot.state.db_session_factory

        async with session_factory() as db_session:
            try:
                await db_session.execute(text("SELECT 1"))
            except Exception as exc:
                return str(exc)
        return None


class RedisHealthCheck(HealthCheckService):
    def __init__(self, request: Request):
        self._request = request

    async def check(self):
        bot: Bot = self._request.app.state.bot
        return await bot.state.redis_repo.ping()


class WorkerHealthCheck(HealthCheckService):
    async def check(self):
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
