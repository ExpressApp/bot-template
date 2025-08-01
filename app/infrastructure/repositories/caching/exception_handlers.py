"""Redis custom exception handlers."""

from redis.asyncio.client import PubSub, PubsubWorkerExceptionHandler

from app.logger import logger


class PubsubExceptionHandler(PubsubWorkerExceptionHandler):
    def __call__(self, exc: BaseException, pubsub: PubSub) -> None:
        logger.exception("Something went wrong in PubSub")
