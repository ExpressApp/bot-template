import warnings
from os import environ
from typing import Callable

import alembic.config
import psycopg2
import pytest


@pytest.fixture()
def migrations():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    alembic.config.main(argv=["upgrade", "head"])
    yield
    alembic.config.main(argv=["downgrade", "base"])
