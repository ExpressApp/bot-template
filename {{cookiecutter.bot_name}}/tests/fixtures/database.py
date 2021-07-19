import warnings
from os import environ
from typing import Callable

import alembic.config
import psycopg2
import pytest

from tests.utils import do_with_retry


@pytest.fixture()
def migrations(postgres_server):
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    alembic.config.main(argv=["upgrade", "head"])
    yield
    alembic.config.main(argv=["downgrade", "base"])


@pytest.fixture(scope="session", autouse=True)
def postgres_server(printer: Callable) -> None:
    db_dsn = environ.get("DB_CONNECTION")
    test_db_dsn = environ.get("TEST_DB_CONNECTION")

    if test_db_dsn:
        db_dsn = test_db_dsn
        printer("using test database")
    else:
        printer("using dev database")  # pragma: no cover

    ping_postgres(db_dsn, printer=printer)
    yield


@do_with_retry(psycopg2.OperationalError, RuntimeError, "cannot start postgres server")
def ping_postgres(dsn: str, *, printer):
    printer(f"pinging db with dsn: {dsn}")
    conn = psycopg2.connect(dsn)
    cur = conn.cursor()
    cur.execute("SELECT now();")
    printer("db pong")
    cur.close()
    conn.close()
