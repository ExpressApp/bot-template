import uuid
from typing import List
from unittest.mock import AsyncMock

import pytest
from botx import Bot, BotXCredentials, SendingCredentials
from botx.clients.methods.errors.user_not_found import UserNotFoundError
from botx.models.users import UserFromSearch

from app.services.botx_user_search import UserIsBotError, search_user_on_each_cts


@pytest.fixture
def user_huid() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def bot_from_search(user_huid: uuid.UUID, host: str) -> UserFromSearch:
    return UserFromSearch(user_huid=user_huid, name="test-bot", emails=[])


@pytest.fixture
def user_from_search(user_huid: uuid.UUID, host: str) -> UserFromSearch:
    return UserFromSearch(user_huid=user_huid, name="test", emails=[])


@pytest.fixture
async def bot_accounts(bot: Bot) -> List[BotXCredentials]:
    return bot.bot_accounts


@pytest.fixture
async def bot_mock() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
async def credentials(host: str, bot_id: uuid.UUID) -> SendingCredentials:
    return SendingCredentials(host=host, bot_id=bot_id)


@pytest.mark.asyncio
async def test_search_user_on_each_cts_found_user(
    bot_mock: AsyncMock,
    user_huid: uuid.UUID,
    credentials: SendingCredentials,
    user_from_search: UserFromSearch,
    host: str,
    bot_accounts: List[BotXCredentials],
):
    bot_mock.search_user.return_value = user_from_search
    user, cts_host = await search_user_on_each_cts(bot_mock, user_huid, bot_accounts)

    bot_mock.search_user.assert_awaited_with(credentials, user_huid=user_huid)
    assert user == user_from_search
    assert cts_host == host


@pytest.mark.asyncio
async def test_search_user_on_each_cts_found_bot(
    bot_mock: AsyncMock,
    user_huid: uuid.UUID,
    credentials: SendingCredentials,
    bot_from_search: UserFromSearch,
    bot_accounts: List[BotXCredentials],
):
    bot_mock.search_user.return_value = bot_from_search
    with pytest.raises(UserIsBotError):
        await search_user_on_each_cts(bot_mock, user_huid, bot_accounts)

    bot_mock.search_user.assert_awaited_with(credentials, user_huid=user_huid)


@pytest.mark.asyncio
async def test_search_user_on_each_cts_exception(
    bot_mock: AsyncMock,
    user_huid: uuid.UUID,
    credentials: SendingCredentials,
    bot_accounts: List[BotXCredentials],
):
    bot_mock.search_user.side_effect = UserNotFoundError()

    with pytest.raises(UserNotFoundError):
        await search_user_on_each_cts(bot_mock, user_huid, bot_accounts)

    bot_mock.search_user.assert_awaited_with(credentials, user_huid=user_huid)
