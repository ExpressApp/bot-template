import asyncio
from datetime import datetime
from typing import Any, Callable, Dict, Optional
from uuid import UUID, uuid4

import jwt
import pytest
from pybotx import (
    BotAccount,
    Chat,
    ChatTypes,
    IncomingMessage,
    UserDevice,
    UserSender,
)
from testcontainers.postgres import PostgresContainer  # type: ignore

from app.settings import settings


@pytest.fixture(scope="session")
def event_loop():
    """Create a session-scoped event loop for async session-scoped fixtures.
    Don't touch this fixture. Its internally used by pytest-asyncio."""
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
def user_huid() -> UUID:
    return UUID("cd069aaa-46e6-4223-950b-ccea42b89c06")


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


@pytest.fixture
def incoming_message_factory(
    bot_id: UUID,
    user_huid: UUID,
    host: str,
) -> Callable[..., IncomingMessage]:
    def factory(
        *,
        body: str = "",
        ad_login: Optional[str] = None,
        ad_domain: Optional[str] = None,
    ) -> IncomingMessage:
        return IncomingMessage(
            bot=BotAccount(
                id=bot_id,
                host=host,
            ),
            sync_id=uuid4(),
            source_sync_id=None,
            body=body,
            data={},
            metadata={},
            sender=UserSender(
                huid=user_huid,
                udid=None,
                ad_login=ad_login,
                ad_domain=ad_domain,
                username=None,
                is_chat_admin=True,
                is_chat_creator=True,
                device=UserDevice(
                    manufacturer=None,
                    device_name=None,
                    os=None,
                    pushes=None,
                    timezone=None,
                    permissions=None,
                    platform=None,
                    platform_package_id=None,
                    app_version=None,
                    locale=None,
                ),
            ),
            chat=Chat(
                id=uuid4(),
                type=ChatTypes.PERSONAL_CHAT,
            ),
            raw_command=None,
        )

    return factory


# @pytest.fixture
# def loguru_caplog(
#     caplog: pytest.LogCaptureFixture,
# ) -> Generator[pytest.LogCaptureFixture, None, None]:
#     # https://github.com/Delgan/loguru/issues/59
#
#     handler_id = logger.add(caplog.handler, format="{message}")
#     yield caplog
#     logger.remove(handler_id)
