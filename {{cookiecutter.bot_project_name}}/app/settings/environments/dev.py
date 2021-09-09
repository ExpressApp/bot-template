"""App settings for development stage."""

from app.settings.environments.base import AppSettings


class DevAppSettings(AppSettings):
    """Application settings with override params for dev environment."""

    # base kwargs
    DEBUG: bool = True
    SQL_DEBUG: bool = True

    # storages
    POSTGRES_DSN: str = (
        "postgresql+asyncpg://postgres:postgres@localhost/"
        "{{ cookiecutter.bot_name_underscored }}"
    )
    REDIS_DSN: str = "redis://localhost/0"

    class Config(AppSettings.Config):  # noqa: WPS431
        env_file = ".env"
