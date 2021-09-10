import alembic.config
import pytest
from sqlalchemy import create_engine

from app.db.sqlalchemy import Base, make_url_sync
from app.settings.environments.test import TestAppSettings


@pytest.mark.db
def test_migrations(settings: TestAppSettings):
    postgres_dsn = make_url_sync(settings.POSTGRES_DSN)
    engine = create_engine(postgres_dsn)
    Base.metadata.drop_all(engine)
    alembic.config.main(argv=["upgrade", "head"])
    alembic.config.main(argv=["downgrade", "base"])
    Base.metadata.create_all(engine)
