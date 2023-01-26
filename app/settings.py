"""Application settings."""

from typing import Any, List
from uuid import UUID

from pybotx import BotAccountWithSecret
from pydantic import BaseSettings


class AppSettings(BaseSettings):
    class Config:  # noqa: WPS431
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

            host, secret_key, bot_id = [
                str_value.strip() for str_value in credentials_str.split("@")
            ]
            return BotAccountWithSecret(
                id=UUID(bot_id), host=host, secret_key=secret_key
            )

    BOT_CREDENTIALS: List[BotAccountWithSecret]

    # base kwargs
    DEBUG: bool = False

    # User huids for debug
    SMARTLOG_DEBUG_HUIDS: List[UUID]

    # database
    POSTGRES_DSN: str
    SQL_DEBUG: bool = False

    # redis
    REDIS_DSN: str

    # healthcheck
    WORKER_TIMEOUT_SEC: float = 4


settings = AppSettings()
