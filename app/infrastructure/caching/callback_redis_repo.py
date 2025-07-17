"""Repository for work callbacks with redis."""

import asyncio
import pickle  # noqa: S403
from typing import Any, Dict, Optional
from uuid import UUID

from pybotx import CallbackNotReceivedError, CallbackRepoProto
from pybotx.bot.exceptions import BotShuttingDownError, BotXMethodCallbackNotFoundError
from pybotx.models.method_callbacks import BotXMethodCallback
from redis.asyncio.client import Redis


class CallbackRedisRepo(CallbackRepoProto):
    """Repository for storing and retrieving BotX method callbacks using Redis Pub/Sub.

    This class allows asynchronous waiting for callbacks by using Redis as a transport
    mechanism and associating each callback with a unique sync_id. It supports setting,
    waiting, and cleaning up callbacks, and handles proper shutdown behavior.
    """

    def __init__(
        self,
        redis: Redis,
        prefix: Optional[str] = None,
    ):
        """Initialize the callback repository with a Redis client.
        Args:
            redis: The Redis client instance.
            prefix: Optional prefix to use for Redis keys.
        """
        self._redis = redis
        self._prefix = prefix or ""
        self._futures: Dict[UUID, asyncio.Future[BotXMethodCallback]] = {}

        self.pubsub = redis.pubsub()

    async def create_botx_method_callback(
        self,
        sync_id: UUID,
    ) -> None:
        """Prepare to receive a callback by subscribing to a Redis channel.

        Args:
            sync_id: Unique identifier for the callback.
        """
        self._futures[sync_id] = asyncio.Future()
        await self.pubsub.subscribe(
            **{self._get_channel_name(sync_id): self._message_handler}
        )

    async def set_botx_method_callback_result(
        self,
        callback: BotXMethodCallback,
    ) -> None:
        """Publish the callback result to Redis.

        Args:
            callback: The callback data to publish.

        Raises:
            BotXMethodCallbackNotFoundError: If no subscriber is listening on the channel.
        """
        dump = pickle.dumps(callback)
        status_code = await self._redis.publish(
            self._get_channel_name(callback.sync_id), dump
        )
        if status_code != 1:
            raise BotXMethodCallbackNotFoundError(sync_id=callback.sync_id)

    async def wait_botx_method_callback(
        self,
        sync_id: UUID,
        timeout: float,
    ) -> BotXMethodCallback:
        """Wait for the callback to be received within a timeout.

        Args:
            sync_id: Unique identifier of the callback.
            timeout: Time to wait for the callback in seconds.

        Returns:
            The received BotXMethodCallback.

        Raises:
            CallbackNotReceivedError: If the callback is not received in time.
        """
        try:
            callback = await asyncio.wait_for(self._futures[sync_id], timeout=timeout)
        except asyncio.TimeoutError:
            raise CallbackNotReceivedError(sync_id) from None
        finally:
            await self.pop_botx_method_callback(sync_id)

        return callback

    async def pop_botx_method_callback(
        self,
        sync_id: UUID,
    ) -> "asyncio.Future[BotXMethodCallback]":
        """Remove the callback from tracking and unsubscribe from Redis.

        Args:
            sync_id: Unique identifier of the callback.

        Returns:
            The future that was associated with the callback.
        """
        await self.pubsub.unsubscribe(self._get_channel_name(sync_id))
        return self._futures.pop(sync_id)

    async def stop_callbacks_waiting(self) -> None:
        """Cancel all pending callbacks due to bot shutdown.

        Sets an exception on all incomplete futures and unsubscribes from Redis.
        """
        await self.pubsub.unsubscribe()

        for sync_id, future in self._futures.items():
            if not future.done():
                future.set_exception(
                    BotShuttingDownError(
                        f"Callback with sync_id `{sync_id!s}` can't be received",
                    ),
                )

    async def _message_handler(self, message: Any) -> None:
        """Handle incoming Redis Pub/Sub messages.

        Deserializes and delivers the callback result to the appropriate future.

        Args:
            message: The message from Redis.
        """
        if message["type"] == "message":
            callback: BotXMethodCallback = pickle.loads(message["data"])  # noqa: S301

            future = self._futures[callback.sync_id]

            if future.done():
                future.result()
            else:
                future.set_result(callback)

    def _get_channel_name(self, sync_id: UUID) -> str:
        """Construct the Redis channel name for a given sync_id.

        Args:
            sync_id: Unique identifier used to correlate the callback.

        Returns:
            A string representing the full Redis channel name.
        """
        return f"{self._prefix}:{sync_id}"
