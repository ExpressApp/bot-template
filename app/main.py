"""Application with configuration for events, routers and middleware."""

import asyncio
from functools import partial

from dependency_injector.wiring import Provide, inject
from fastapi import FastAPI
from pybotx import Bot
from redis import asyncio as aioredis
from redis.asyncio import Redis

import tests.integration.conftest
from app.infrastructure.repositories.caching.callback_redis_repo import (
    CallbackRedisRepo,
)
from app.infrastructure.repositories.caching.exception_handlers import (
    PubsubExceptionHandler,
)
from app.infrastructure.repositories.caching.redis_repo import RedisRepo
from app.infrastructure.containers import (
    ApplicationStartupContainer,
    BotSampleRecordCommandContainer,
    CallbackTaskManager,
)
from app.infrastructure.db.sqlalchemy import close_db_connections
from app.logger import logger
from app.presentation.api.routers import router
from app.presentation.bot.bot import get_bot
from app.presentation.bot.resources import strings
from app.settings import settings


async def startup(
    bot: Bot = Provide[ApplicationStartupContainer.bot],
) -> None:
    await bot.startup()


async def shutdown(
    callback_task_manager: CallbackTaskManager = Provide[
        ApplicationStartupContainer.callback_task_manager
    ],
    bot: Bot = Provide[ApplicationStartupContainer.bot],
    redis_client: Redis = Provide[ApplicationStartupContainer.redis_client],
) -> None:
    await bot.shutdown()

    await callback_task_manager.shutdown()

    await redis_client.aclose()
    await close_db_connections()


def get_application() -> FastAPI:
    """Create configured server application instance."""

    # Initialize the main application container
    main_container = ApplicationStartupContainer()
    main_container.wire(modules=["app.main", "app.presentation.api.botx"])

    # Initialize the SampleRecord commands container
    sample_record_commands_container = BotSampleRecordCommandContainer()
    sample_record_commands_container.wire(
        modules=["app.presentation.bot.commands.sample_record"]
    )

    application = FastAPI(title=strings.BOT_PROJECT_NAME, openapi_url=None)

    # put bot to state for tests
    application.state.bot = main_container.bot()

    application.add_event_handler(
        "startup",
        partial(startup, bot=main_container.bot()),
    )
    application.add_event_handler(
        "shutdown",
        partial(
            shutdown,
            callback_task_manager=main_container.callback_task_manager(),
            bot=main_container.bot(),
            redis_client=main_container.redis_client(),
        ),
    )

    application.include_router(router)

    return application
