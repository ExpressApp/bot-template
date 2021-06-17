"""Environments configuration and reading for usage in any part of application."""
from functools import lru_cache
from typing import Dict, Type

from app.settings.environments.base import AppEnvTypes, AppSettings, BaseAppSettings
from app.settings.environments.dev import DevAppSettings
from app.settings.environments.prod import ProdAppSettings
from app.settings.environments.test import TestAppSettings

environments: Dict[str, Type[AppSettings]] = {
    AppEnvTypes.PROD: ProdAppSettings,
    AppEnvTypes.DEV: DevAppSettings,
    AppEnvTypes.TEST: TestAppSettings,
}


@lru_cache()
def get_app_settings() -> AppSettings:
    """
    Return cached instance of the AppSettings object.

    Missing vars reading from .env for every APP_ENV.

    """

    app_env = BaseAppSettings().APP_ENV
    config = environments[app_env]
    return config()
