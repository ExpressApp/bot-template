import alembic.config
import pytest
from sqlalchemy import create_engine

from app.db.sqlalchemy import Base, make_url_sync
from app.settings.environments.test import TestAppSettings


@pytest.mark.db
def test_migrations(settings: TestAppSettings):
    dsn = settings.DATABASE_URL
    engine = create_engine(make_url_sync(dsn))
    Base.metadata.drop_all(engine)
    alembic.config.main(argv=["upgrade", "head"])
    alembic.config.main(argv=["downgrade", "base"])
