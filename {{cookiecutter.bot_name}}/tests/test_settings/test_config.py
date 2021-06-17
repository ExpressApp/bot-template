import pytest
from pydantic import ValidationError

from app.settings.environments.test import AppSettings


def test_credentions_validation():
    AppSettings(
        DEBUG=True,
        SQL_DEBUG=True,
        BOT_CREDENTIALS="any@secret@d633a0c0-5c5d-41de-b7f9-5ba7e8a34550",
        DATABASE_URL="postgres://postgres:postgres@localhost/postgres",
        REDIS_DSN="redis://localhost/0",
    )
    with pytest.raises(ValidationError):
        AppSettings(
            DEBUG=True,
            SQL_DEBUG=True,
            BOT_CREDENTIALS=None,
            DATABASE_URL="postgres://postgres:postgres@localhost/postgres",
            REDIS_DSN="redis://localhost/0",
        )
