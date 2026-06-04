"""Application settings."""

from typing import Annotated, Any, List
from uuid import UUID

from pybotx import BotAccountWithSecret
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("BOT_CREDENTIALS", mode="before")
    @classmethod
    def parse_bot_credentials(cls, raw_val: Any) -> List[BotAccountWithSecret]:
        if not raw_val:
            return []

        if isinstance(raw_val, str):
            return [
                cls._build_credentials_from_string(credentials_str)
                for credentials_str in raw_val.replace(",", " ").split()
            ]

        return raw_val

    @field_validator("SMARTLOG_DEBUG_HUIDS", mode="before")
    @classmethod
    def parse_smartlog_debug_huids(cls, raw_huids: Any) -> List[UUID]:
        """Parse debug huids separated by comma."""
        if not raw_huids:
            return []

        if isinstance(raw_huids, str):
            return [UUID(huid.strip()) for huid in raw_huids.split(",")]

        return raw_huids

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
            id=UUID(bot_id), cts_url=AnyHttpUrl(cts_url), secret_key=secret_key
        )

    BOT_CREDENTIALS: Annotated[List[BotAccountWithSecret], NoDecode]

    # base kwargs
    DEBUG: bool = False

    # User huids for debug
    SMARTLOG_DEBUG_HUIDS: Annotated[List[UUID], NoDecode]

    # database
    POSTGRES_DSN: str
    SQL_DEBUG: bool = False

    # redis
    REDIS_DSN: str
    CONNECTION_POOL_SIZE: int = 10

    # healthcheck
    WORKER_TIMEOUT_SEC: float = 4


settings = AppSettings()  # type: ignore[call-arg]
