import alembic.config
import pytest
import warnings


@pytest.fixture
def skip_unraisable():
    warnings.filterwarnings("ignore", category=pytest.PytestUnraisableExceptionWarning)


@pytest.mark.db
def test_migrations(skip_unraisable):
    alembic.config.main(argv=["upgrade", "head"])
    alembic.config.main(argv=["downgrade", "base"])
