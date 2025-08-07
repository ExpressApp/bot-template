import asyncio
from datetime import datetime
from typing import Any, Dict
from uuid import UUID

import jwt
import pytest

from app.settings import settings


@pytest.fixture(scope="session")
def event_loop():
    """Create a session-scoped event loop for async session-scoped fixtures.
    Don't touch this fixture. It's internally used by pytest-asyncio."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture
def bot_id() -> UUID:
    return settings.BOT_CREDENTIALS[0].id


@pytest.fixture
def host() -> str:
    return settings.BOT_CREDENTIALS[0].host


@pytest.fixture
def secret_key() -> str:
    return settings.BOT_CREDENTIALS[0].secret_key


@pytest.fixture
def authorization_token_payload(bot_id: UUID, host: str) -> Dict[str, Any]:
    return {
        "aud": [str(bot_id)],
        "exp": datetime(year=3000, month=1, day=1).timestamp(),
        "iat": datetime(year=2000, month=1, day=1).timestamp(),
        "iss": host,
        "jti": "2uqpju31h6dgv4f41c005e1i",
        "nbf": datetime(year=2000, month=1, day=1).timestamp(),
    }


@pytest.fixture
def authorization_header(
    secret_key: str,
    authorization_token_payload: Dict[str, Any],
) -> Dict[str, str]:
    token = jwt.encode(
        payload=authorization_token_payload,
        key=secret_key,
    )
    return {"authorization": f"Bearer {token}"}
