from os import environ
import warnings
import pytest
from sqlalchemy import create_engine

from app.db.sqlalchemy import Base, make_url_sync


@pytest.fixture
def migrations(printer):
    warnings.filterwarnings("ignore", category=ResourceWarning)
    dsn = environ.get("TEST_DB_CONNECTION")
    if dsn:
        printer(f"Using database {dsn}")
        engine = create_engine(make_url_sync(dsn))
        Base.metadata.create_all(engine)
        yield
        Base.metadata.drop_all(engine)
    else:
        yield
