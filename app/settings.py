"""Application settings."""

from typing import Any, List
from uuid import UUID

from pybotx import BotAccountWithSecret
from pydantic import Field, PositiveInt, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # base kwargs
    DEBUG: bool = False

    BOT_CREDENTIALS: list[BotAccountWithSecret] | str

    # hide original exceptions from bot user
    RAISE_BOT_EXCEPTIONS: bool = False

    # User huids for debug
    SMARTLOG_DEBUG_HUIDS: List[UUID] | str

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

    BOTX_CALLBACK_TIMEOUT_IN_SECONDS: int = 30
    BOT_ASYNC_CLIENT_TIMEOUT_IN_SECONDS: int = 60

    @field_validator("SMARTLOG_DEBUG_HUIDS", mode="before")
    @classmethod
    def parse_smartlog_debug_huids(cls, v):
        if not v:
            return []
        return [UUID(huid) for huid in v.split(",")]

    @field_validator("BOT_CREDENTIALS", mode="before")
    @classmethod
    def parse_bot_credentials(cls, v):
        if not v:
            return []
        # parse your raw env string here
        return [
            cls._build_credentials_from_string(credentials_str)
            for credentials_str in v.replace(",", " ").split()
        ]

    @classmethod
    def _build_credentials_from_string(
        cls, credentials_str: str
    ) -> BotAccountWithSecret:
        credentials_str = credentials_str.replace("|", "@")

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


settings = AppSettings()  # type: ignore[call-arg]
