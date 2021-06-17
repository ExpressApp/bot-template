"""App settings for prod stage."""

from pydantic import Field, PostgresDsn, RedisDsn

from app.settings.environments.base import AppSettings


class ProdAppSettings(AppSettings):
    """Application settings with override params for production environment."""

    # base kwargs
    DEBUG: bool = False
    SQL_DEBUG: bool = False

    # storages
    DATABASE_URL: PostgresDsn = Field(..., env="DB_CONNECTION")
    REDIS_DSN: RedisDsn

    class Config(AppSettings.Config):  # noqa: WPS431
        env_file = "prod.env"
