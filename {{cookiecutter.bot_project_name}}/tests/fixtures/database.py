import warnings
from typing import Callable

import pytest
from sqlalchemy import create_engine

from app.db.sqlalchemy import Base, make_url_sync
from app.settings.environments.test import TestAppSettings


@pytest.fixture
def migrations(printer: Callable, settings: TestAppSettings):
    import app.db.models  # isort: skip

    warnings.filterwarnings("ignore", category=ResourceWarning)
    postgres_dsn = settings.POSTGRES_DSN
    printer(f"Using database {postgres_dsn}")

    engine = create_engine(make_url_sync(postgres_dsn))
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)
