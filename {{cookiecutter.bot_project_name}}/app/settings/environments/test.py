"""App settings for test stage."""
from typing import Any, List

from botx import BotXCredentials
from pydantic import validator

from app.settings.environments.base import AppSettings


class TestAppSettings(AppSettings):
    """Application settings with override params for test environment."""

    # base kwargs
    DEBUG: bool = True
    SQL_DEBUG: bool = True
    BOT_CREDENTIALS: Any = "cts.example.com@secret@123e4567-e89b-12d3-a456-426655440000"

    # storages
    POSTGRES_DSN: str = (
        "postgresql://postgres:postgres@localhost/"
        "{{ cookiecutter.bot_name_underscored }}_test"
    )
    REDIS_DSN: str = "redis://localhost/0"

    class Config(AppSettings.Config):  # noqa: WPS431
        env_file = ".env"

    @validator("BOT_CREDENTIALS", pre=True)
    @classmethod
    def parse_bot_credentials(cls, raw_credentials: Any) -> List[BotXCredentials]:
        """Parse bot credentials separated by comma.

        If passed empty string return empty list for test env.
        """
        try:
            return super().parse_bot_credentials(raw_credentials)
        except ValueError:
            return []
