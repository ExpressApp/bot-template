"""Redis custom exception handlers."""

from redis.asyncio.client import PubSub

from app.logger import logger


async def pubsub_exception_handler(exc: BaseException, pubsub: PubSub) -> None:
    logger.exception("Something went wrong in PubSub")
