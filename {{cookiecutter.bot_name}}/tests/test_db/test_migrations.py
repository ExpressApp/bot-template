import alembic.config
import pytest
from sqlalchemy import create_engine
from os import environ
from app.db.sqlalchemy import Base, make_url_sync


@pytest.mark.db
def test_migrations():
    dsn = environ.get("TEST_DB_CONNECTION")
    engine = create_engine(make_url_sync(dsn))
    Base.metadata.drop_all(engine)
    alembic.config.main(argv=["upgrade", "head"])
    alembic.config.main(argv=["downgrade", "base"])
