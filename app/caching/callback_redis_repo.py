"""Repository for work callbacks with redis."""

import asyncio
import pickle  # noqa: S403
from typing import Dict, Optional
from uuid import UUID

from pybotx import CallbackNotReceivedError, CallbackRepoProto
from pybotx.bot.exceptions import BotShuttingDownError, BotXMethodCallbackNotFoundError
from pybotx.models.method_callbacks import BotXMethodCallback
from redis import asyncio as aioredis


class CallbackRedisRepo(CallbackRepoProto):
    def __init__(
        self,
        redis: aioredis.Redis,
        prefix: Optional[str] = None,
    ):
        self._redis = redis
        self._prefix = prefix or ""
        self._pubsubs: Dict[UUID, aioredis.client.PubSub] = {}
        self._futures: Dict[UUID, asyncio.Future] = {}

    async def create_botx_method_callback(
        self,
        sync_id: UUID,
    ) -> None:
        pubsub = self._redis.pubsub()
        await pubsub.subscribe(f"{self._prefix}:{sync_id}")
        self._futures[sync_id] = asyncio.Future()
        self._pubsubs[sync_id] = pubsub

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
        channel = self._get_pubsub(sync_id)
        try:
            callback = await asyncio.wait_for(
                self._get_callback(channel), timeout=timeout
            )
        except asyncio.TimeoutError:
            raise CallbackNotReceivedError(sync_id) from None

        future = self._futures[sync_id]
        if future.done():
            future.result()
        else:
            future.set_result(callback)

        return callback

    async def pop_botx_method_callback(
        self,
        sync_id: UUID,
    ) -> "asyncio.Future[BotXMethodCallback]":
        return self._futures[sync_id]

    async def stop_callbacks_waiting(self) -> None:
        for pubsub in self._pubsubs.values():
            await pubsub.unsubscribe()

        for sync_id, future in self._futures.items():
            if not future.done():
                future.set_exception(
                    BotShuttingDownError(
                        f"Callback with sync_id `{sync_id!s}` can't be received",
                    ),
                )

    def _get_pubsub(self, sync_id: UUID) -> aioredis.client.PubSub:
        try:
            return self._pubsubs[sync_id]
        except KeyError:
            raise BotXMethodCallbackNotFoundError(sync_id) from None

    @classmethod
    async def _get_callback(  # type: ignore
        cls,
        channel: aioredis.client.PubSub,
    ) -> BotXMethodCallback:
        async for message in channel.listen():
            if message["type"] == "message":
                return pickle.loads(message["data"])  # noqa: S301
