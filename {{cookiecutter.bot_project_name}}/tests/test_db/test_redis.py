import pytest

from app.db.redis.repo import RedisRepo
from app.settings.config import get_app_settings

config = get_app_settings()


@pytest.fixture
async def redis_repo() -> RedisRepo:
    redis_repo = await RedisRepo.init(dsn=config.REDIS_DSN)
    yield redis_repo
    await redis_repo.close()


@pytest.fixture
async def redis_repo_with_prefix() -> RedisRepo:
    redis_repo = await RedisRepo.init(dsn=config.REDIS_DSN, prefix="test")
    yield redis_repo
    await redis_repo.close()


@pytest.fixture
async def key_str() -> str:
    return "key"


@pytest.fixture
async def test_value_str() -> str:
    return "test_value"


@pytest.fixture
async def key(key_str: str) -> str:
    return "79e10f7d50e107f13d27091485187c60"


@pytest.fixture
async def prefix_key(redis_repo_with_prefix: RedisRepo, key: str) -> str:
    return "test_79e10f7d50e107f13d27091485187c60"


@pytest.fixture
async def test_value(test_value_str: str) -> bytes:
    return b"\x80\x04\x95\x0e\x00\x00\x00\x00\x00\x00\x00\x8c\ntest_value\x94."


@pytest.mark.asyncio
async def test_setting_value_redis(
    redis_repo: RedisRepo,
    key: str,
    test_value: bytes,
    key_str: str,
    test_value_str: str,
):
    await redis_repo.set(key_str, test_value_str)

    assert await redis_repo.redis.get(key) == test_value


@pytest.mark.asyncio
async def test_getting_value_redis(
    redis_repo: RedisRepo,
    key: str,
    test_value: bytes,
    key_str: str,
    test_value_str: str,
):
    await redis_repo.redis.set(key, test_value)

    assert await redis_repo.get(key_str) == test_value_str


@pytest.mark.asyncio
async def test_removing_and_getting_value_redis(
    redis_repo_with_prefix: RedisRepo,
    prefix_key: str,
    test_value: bytes,
    key_str: str,
    test_value_str: str,
):
    await redis_repo_with_prefix.redis.set(prefix_key, test_value)

    assert await redis_repo_with_prefix.rget(key_str) == test_value_str
    assert await redis_repo_with_prefix.redis.get(prefix_key) is None


@pytest.mark.asyncio
async def test_getting_default_value_redis(
    redis_repo_with_prefix: RedisRepo,
    key_str: str,
    test_value_str: str,
):
    assert await redis_repo_with_prefix.get(key_str, test_value_str) == test_value_str
