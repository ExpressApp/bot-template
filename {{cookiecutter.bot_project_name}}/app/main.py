"""Application with configuration for events, routers and middleware."""

from functools import partial
from typing import Optional

from fastapi import FastAPI
from pybotx import Bot, CallbackRepoProto
from redis import asyncio as aioredis

from app.api.routers import router
from app.bot.bot import get_bot
from app.caching.redis_repo import RedisRepo
from app.db.sqlalchemy import build_db_session_factory
from app.resources import strings
from app.settings import settings


async def startup(bot: Bot) -> None:
    # -- Bot --
    await bot.startup()

    # -- Database --
    bot.state.db_session_factory = await build_db_session_factory()

    # -- Redis --
    bot.state.redis = aioredis.from_url(settings.REDIS_DSN)
    bot.state.redis_repo = RedisRepo(
        redis=bot.state.redis, prefix=strings.BOT_PROJECT_NAME
    )


async def shutdown(bot: Bot) -> None:
    # -- Bot --
    await bot.shutdown()

    # -- Redis --
    await bot.state.redis.close()


def get_application(
    add_internal_error_handler: bool = True,
    callback_repo: Optional[CallbackRepoProto] = None,
) -> FastAPI:
    """Create configured server application instance."""

    bot = get_bot(add_internal_error_handler, callback_repo)

    application = FastAPI(title=strings.BOT_PROJECT_NAME, openapi_url=None)
    application.state.bot = bot

    application.add_event_handler("startup", partial(startup, bot))
    application.add_event_handler("shutdown", partial(shutdown, bot))

    application.include_router(router)

    return application

app = get_application()
