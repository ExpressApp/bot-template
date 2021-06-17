"""Functions to create and close connections to db."""
from typing import Optional

from databases import DatabaseURL
from starlette.datastructures import URL
from tortoise import Tortoise

from app.db.redis.repo import RedisRepo


async def init_db(dsn: DatabaseURL) -> None:
    """Create connection to db and init orm models."""
    await Tortoise.init(db_url=str(dsn), modules={"botx": ["app.db.botx.models"]})


async def init_redis(
    redis_dsn: URL, prefix: Optional[str] = None, expire: Optional[int] = None
) -> RedisRepo:
    """Create connection to redis."""

    return await RedisRepo.init(dsn=redis_dsn, prefix=prefix, expire=expire)


async def close_redis(redis: Optional[RedisRepo]) -> None:
    """Close redis connections."""
    if redis:
        await redis.close()


async def close_db() -> None:
    """Close connection to db."""
    await Tortoise.close_connections()
