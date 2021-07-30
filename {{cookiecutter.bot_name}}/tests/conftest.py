import random
import string
import uuid

import httpx
import pytest
from asgi_lifespan import LifespanManager
from botx import Bot, BotXCredentials, ChatCreatedEvent
from botx.testing import MessageBuilder, TestClient
from fastapi import FastAPI
from pytest_cov.plugin import StoreReport

from app.settings.environments.test import TestAppSettings

pytest_plugins = ["tests.fixtures.printer", "tests.fixtures.database"]


def pytest_addoption(parser):
    """Add options to control coverage."""

    def fake_validate_report(_):  # pragma: no cover
        return "term-missing", "skip-covered"

    group = parser.getgroup(
        "cov", "coverage reporting with distributed testing support"
    )
    group.addoption(
        "--poco",
        action=StoreReport,
        type=fake_validate_report,
        help="Short alias for option term-missing:skip-covered",
    )


@pytest.fixture
def settings() -> TestAppSettings:
    return TestAppSettings()


@pytest.fixture
def app(migrations) -> FastAPI:
    from app.main import get_application

    return get_application()


@pytest.fixture(autouse=True)
async def http_client(app: FastAPI) -> httpx.AsyncClient:
    async with LifespanManager(app):
        async with httpx.AsyncClient(
            base_url="http://testserver", app=app
        ) as app_client:
            yield app_client


@pytest.fixture(autouse=True)
async def botx_client(bot: Bot) -> TestClient:
    with TestClient(bot) as client:
        yield client


@pytest.fixture
def secret_key() -> str:
    return "secret"


@pytest.fixture
def bot(app: FastAPI, builder: MessageBuilder, secret_key: str) -> Bot:
    bot_app = app.state.bot
    bot_app.bot_accounts = [
        BotXCredentials(
            host=builder.user.host, secret_key=secret_key, bot_id=builder.bot_id
        )
    ]
    return bot_app


@pytest.fixture
def builder(bot_id: uuid.UUID, host: str, group_chat_id: uuid.UUID) -> MessageBuilder:
    builder = MessageBuilder(bot_id=bot_id)
    builder.user.host = host
    builder.user.group_chat_id = group_chat_id
    return builder


@pytest.fixture(scope="session")
def bot_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture(scope="session")
def host() -> str:
    return "cts.testing.dev"


@pytest.fixture()
def group_chat_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def chat_created_data() -> ChatCreatedEvent:
    def generate_acsii_name() -> str:
        return "".join(
            random.choice(string.ascii_lowercase) for i in range(random.randint(5, 10))
        )

    def generate_username() -> str:
        return " ".join(
            (generate_acsii_name().capitalize(), generate_acsii_name().capitalize())
        )

    creator_huid = uuid.uuid4()
    users = [
        {
            "huid": uuid.uuid4(),
            "user_kind": random.choice(["user", "botx"]),
            "name": generate_username(),
            "admin": random.choice([True, False]),
        }
        for _ in range(random.randrange(2, 6))
    ]
    users.append(
        {
            "huid": creator_huid,
            "user_kind": "user",
            "name": generate_username(),
            "admin": True,
        }
    )
    users.append(
        {
            "huid": uuid.uuid4(),
            "user_kind": "botx",
            "name": generate_username(),
            "admin": False,
        }
    )

    return ChatCreatedEvent(
        **{
            "group_chat_id": uuid.uuid4(),
            "chat_type": "group_chat",
            "name": "Test Chat",
            "creator": creator_huid,
            "members": users,
        }
    )
