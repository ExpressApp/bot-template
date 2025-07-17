"""Repository for work with redis."""

import hashlib
import pickle  # noqa: S403
from typing import Any, Hashable, Optional

from redis import asyncio as aioredis


class RedisRepo:
    def __init__(
        self,
        redis: aioredis.Redis,
        prefix: Optional[str] = None,
        expire: Optional[int] = None,
    ) -> None:
        self._redis = redis
        self._prefix = prefix
        self._expire = expire
        self._delimiter = "_"

    async def ping(self) -> Optional[str]:
        try:
            await self._redis.ping()
        except Exception as exc:
            return str(exc)

        return None

    async def get(self, key: Hashable, default: Any = None) -> Any:
        cached_data = await self._redis.get(self._key(key))
        if cached_data is None:
            return default

        return pickle.loads(cached_data)  # noqa: S301

    async def set(
        self, key: Hashable, storage_value: Any, expire: Optional[int] = None
    ) -> None:
        if expire is None:
            expire = self._expire

        dumps = pickle.dumps(storage_value)
        await self._redis.set(self._key(key), dumps, ex=expire)

    async def delete(self, key: Hashable) -> None:
        await self._redis.delete(self._key(key))

    async def rget(self, key: Hashable, default: Any = None) -> Any:
        storage_value = await self.get(key, default)
        await self.delete(key)
        return storage_value

    def _key(self, arg: Hashable) -> str:
        if self._prefix is not None:
            prefix = self._prefix + self._delimiter
        else:
            prefix = ""

        return prefix + hashlib.md5(pickle.dumps(arg)).hexdigest()  # noqa: S303
