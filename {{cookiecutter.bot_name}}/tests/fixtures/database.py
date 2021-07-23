import warnings

import pytest
from sqlalchemy import create_engine

from app.db.sqlalchemy import Base, make_url_sync
from app.settings.environments.test import TestAppSettings


@pytest.fixture
def migrations(printer, settings: TestAppSettings):
    import app.db.models  # isort: skip

    warnings.filterwarnings("ignore", category=ResourceWarning)
    dsn = settings.DATABASE_URL
    printer(f"Using database {dsn}")

    engine = create_engine(make_url_sync(dsn))
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)
