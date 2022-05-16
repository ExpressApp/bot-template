"""Repository for work with redis."""

import hashlib
import pickle  # noqa: S403
from typing import Any, Hashable, Optional

import aioredis


class RedisRepo:
    redis: aioredis.Redis
    dsn: str
    prefix: Optional[str]
    delimiter: str
    expire: Optional[int]

    def __init__(
        self, dsn: str, prefix: Optional[str] = None, expire: Optional[int] = None
    ) -> None:
        """Init repository object."""

        self.dsn = str(dsn)
        self.prefix = prefix
        self.expire = expire
        self.delimiter = "_"

    @classmethod
    async def init(
        cls, dsn: str, prefix: Optional[str] = None, expire: Optional[int] = None
    ) -> "RedisRepo":
        """Init repository object."""

        repo = cls(dsn=dsn, prefix=prefix, expire=expire)
        repo.redis = await aioredis.create_redis_pool(repo.dsn)
        return repo

    async def ping(self) -> Optional[str]:
        """Healthcheck the redis server."""

        try:
            await self.redis.ping(message="ping", encoding="utf-8")
        except Exception as exc:
            return str(exc)

        return None

    async def close(self) -> None:
        """Close connection to redis."""

        self.redis.close()
        await self.redis.wait_closed()

    async def get(self, key: Hashable, default: Any = None) -> Any:
        """Get value from redis."""

        cached_data = await self.redis.get(self._key(key))
        if cached_data is None:
            return default

        return pickle.loads(cached_data)  # noqa: S301

    async def set(
        self, key: Hashable, storage_value: Any, expire: Optional[int] = None
    ) -> None:
        """Set value into redis."""

        if expire is None:
            expire = self.expire

        dumps = pickle.dumps(storage_value)
        await self.redis.set(self._key(key), dumps, expire=expire)

    async def delete(self, key: Hashable) -> None:
        """Remove value from redis."""

        await self.redis.delete(self._key(key))

    async def rget(self, key: Hashable, default: Any = None) -> Any:
        """Get value and remove it from redis."""

        storage_value = await self.get(key, default)
        await self.delete(key)
        return storage_value

    def _key(self, arg: Hashable) -> str:
        if self.prefix is not None:
            prefix = self.prefix + self.delimiter
        else:
            prefix = ""

        return prefix + hashlib.md5(pickle.dumps(arg)).hexdigest()  # noqa: S303
