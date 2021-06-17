"""
Functions wrappers for startup and shutdown events for server.

For more info see https://fastapi.tiangolo.com/advanced/events/
"""
from typing import Callable

from botx import Bot
from databases import DatabaseURL

from app.db.events import close_db, close_redis, init_db, init_redis
from app.settings.logger import configure_logger


def startup(
    db_dsn: DatabaseURL, redis_dsn: DatabaseURL, redis_prefix: str, bot_app: Bot
) -> Callable:
    """
    Create startup event handler.

    Should be run before the app starts. Here should be init for db, redis, etc.
    """

    async def start_app() -> None:  # noqa: WPS430
        configure_logger()
        await bot_app.start()
        await init_db(db_dsn)
        bot_app.state.redis = await init_redis(redis_dsn, redis_prefix)

        await bot_app.authorize()

    return start_app


def shutdown(bot_app: Bot) -> Callable:
    """
    Shutdown event handler.

    Should be run when the app is shutting down. Here should close db, redis, etc.
    """

    async def stop_app() -> None:  # noqa: WPS430
        await bot_app.shutdown()
        await close_db()
        await close_redis(bot_app.state.redis)
        await bot_app.state.redis.close()

    return stop_app
