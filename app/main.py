"""Application with configuration for events, routers and middleware."""

import asyncio
from functools import partial

from dependency_injector.wiring import Provide
from fastapi import FastAPI
from pybotx import Bot
from redis import asyncio as aioredis
from redis.asyncio import Redis

from app.infrastructure.caching.callback_redis_repo import CallbackRedisRepo
from app.infrastructure.caching.exception_handlers import PubsubExceptionHandler
from app.infrastructure.caching.redis_repo import RedisRepo
from app.infrastructure.containers import ApplicationStartupContainer
from app.infrastructure.db.sqlalchemy import close_db_connections
from app.presentation.api.routers import router
from app.presentation.bot.bot import get_bot
from app.presentation.bot.resources import strings
from app.settings import settings


async def startup(
    application: FastAPI,
    raise_bot_exceptions: bool,
    redis_client: Redis = Provide[ApplicationStartupContainer.redis_client],
    redis_repo: RedisRepo = Provide[ApplicationStartupContainer.redis_repo],
) -> None:
    pool = aioredis.BlockingConnectionPool(
        max_connections=settings.REDIS_CONNECTION_POOL_SIZE,
        **redis_client.connection_pool.connection_kwargs,
    )
    redis_client.connection_pool = pool

    # -- Bot --
    callback_repo = CallbackRedisRepo(redis_client)
    process_callbacks_task = asyncio.create_task(
        callback_repo.pubsub.run(exception_handler=PubsubExceptionHandler())
    )
    bot = get_bot(callback_repo, raise_exceptions=raise_bot_exceptions)

    await bot.startup()

    # bot.state.db_session_factory = db_session_factory
    bot.state.redis_repo = redis_repo

    application.state.bot = bot
    application.state.redis = redis_client
    application.state.process_callbacks_task = process_callbacks_task


async def shutdown(application: FastAPI) -> None:
    # -- Bot --
    bot: Bot = application.state.bot
    await bot.shutdown()
    process_callbacks_task: asyncio.Task = application.state.process_callbacks_task
    process_callbacks_task.cancel()
    await asyncio.gather(process_callbacks_task, return_exceptions=True)

    # -- Redis --
    redis_client: aioredis.Redis = application.state.redis
    await redis_client.close()

    # -- Database --
    await close_db_connections()


def get_application(raise_bot_exceptions: bool = False) -> FastAPI:
    """Create configured server application instance."""

    # Initialize the container
    container = ApplicationStartupContainer()
    container.wire(modules=["app.main"])

    application = FastAPI(title=strings.BOT_PROJECT_NAME, openapi_url=None)

    application.add_event_handler(
        "startup", partial(startup, application, raise_bot_exceptions)
    )
    application.add_event_handler("shutdown", partial(shutdown, application))

    application.include_router(router)

    return application
