"""App settings for prod stage."""

from app.settings.environments.base import AppSettings


class ProdAppSettings(AppSettings):
    """Application settings with override params for production environment."""

    # base kwargs
    DEBUG: bool = False
    SQL_DEBUG: bool = False

    # storages
    POSTGRES_DSN: str
    REDIS_DSN: str

    class Config(AppSettings.Config):  # noqa: WPS431
        env_file = "prod.env"
