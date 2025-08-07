"""Application settings."""

from typing import Any, List
from uuid import UUID

from pybotx import BotAccountWithSecret
from pydantic import BaseSettings, Field, PositiveInt


class AppSettings(BaseSettings):
    class Config:
        env_file = ".env"

        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str) -> Any:
            if field_name == "BOT_CREDENTIALS":
                if not raw_val:
                    return []

                return [
                    cls._build_credentials_from_string(credentials_str)
                    for credentials_str in raw_val.replace(",", " ").split()
                ]
            elif field_name == "SMARTLOG_DEBUG_HUIDS":
                return cls.parse_smartlog_debug_huids(raw_val)

            return cls.json_loads(raw_val)  # type: ignore

        @classmethod
        def parse_smartlog_debug_huids(cls, raw_huids: Any) -> List[UUID]:
            """Parse debug huids separated by comma."""
            if not raw_huids:
                return []

            return [UUID(huid) for huid in raw_huids.split(",")]

        @classmethod
        def _build_credentials_from_string(
            cls, credentials_str: str
        ) -> BotAccountWithSecret:
            credentials_str = credentials_str.replace("|", "@")
            assert credentials_str.count("@") == 2, "Have you forgot to add `bot_id`?"

            cts_url, secret_key, bot_id = [
                str_value.strip() for str_value in credentials_str.split("@")
            ]

            if "://" not in cts_url:
                cts_url = f"https://{cts_url}"

            return BotAccountWithSecret(
                id=UUID(bot_id),
                cts_url=cts_url,  # type: ignore[arg-type]
                secret_key=secret_key,
            )

    BOT_CREDENTIALS: List[BotAccountWithSecret]

    # base kwargs
    DEBUG: bool = False

    # hide original exceptions from bot user
    RAISE_BOT_EXCEPTIONS: bool = False

    # User huids for debug
    SMARTLOG_DEBUG_HUIDS: List[UUID]

    # database
    POSTGRES_DSN: str
    DB_ENGINE_POOL_SIZE: PositiveInt = 4
    DB_ENGINE_MAX_OVERFLOW: int = Field(ge=-1, default=10)
    DB_ENGINE_POOL_RECYCLE: int = Field(ge=-1, default=60 * 60)  # 1 hour

    SQL_DEBUG: bool = False

    # redis
    REDIS_DSN: str
    REDIS_CONNECTION_POOL_SIZE: int = 10

    # worker
    WORKER_CONCURRENCY: int = 2
    WORKERS_COUNT: int = 1

    BOTX_CALLBACK_TIMEOUT_IN_SECONDS = 30
    BOT_ASYNC_CLIENT_TIMEOUT_IN_SECONDS = 60


settings = AppSettings()  # type: ignore[call-arg]
