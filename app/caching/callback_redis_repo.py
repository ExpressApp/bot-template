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
    def __init__(
        self,
        redis: Redis,
        prefix: Optional[str] = None,
    ):
        self._redis = redis
        self._prefix = prefix or ""
        self._futures: Dict[UUID, asyncio.Future[BotXMethodCallback]] = {}

        self.pubsub = redis.pubsub()

    async def create_botx_method_callback(
        self,
        sync_id: UUID,
    ) -> None:
        self._futures[sync_id] = asyncio.Future()
        await self.pubsub.subscribe(
            **{f"{self._prefix}:{sync_id}": self._message_handler}
        )

    async def set_botx_method_callback_result(
        self,
        callback: BotXMethodCallback,
    ) -> None:
        dump = pickle.dumps(callback)
        status_code = await self._redis.publish(
            f"{self._prefix}:{callback.sync_id}", dump
        )
        if status_code != 1:
            raise BotXMethodCallbackNotFoundError(sync_id=callback.sync_id)

    async def wait_botx_method_callback(
        self,
        sync_id: UUID,
        timeout: float,
    ) -> BotXMethodCallback:
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
        await self.pubsub.unsubscribe(f"{self._prefix}:{sync_id}")
        return self._futures.pop(sync_id)

    async def stop_callbacks_waiting(self) -> None:
        await self.pubsub.unsubscribe()

        for sync_id, future in self._futures.items():
            if not future.done():
                future.set_exception(
                    BotShuttingDownError(
                        f"Callback with sync_id `{sync_id!s}` can't be received",
                    ),
                )

    async def _message_handler(self, message: Any) -> None:
        if message["type"] == "message":
            callback: BotXMethodCallback = pickle.loads(message["data"])  # noqa: S301

            future = self._futures[callback.sync_id]

            if future.done():
                future.result()
            else:
                future.set_result(callback)
