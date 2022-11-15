from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from pybotx import Bot, UserFromSearch, UserKinds, UserNotFoundError

from app.services.botx_user_search import UserIsBotError, search_user_on_each_cts


async def test_search_user_on_each_cts_user_is_bot_error_raised(
    bot: Bot,
) -> None:
    # - Arrange -
    bot_user = UserFromSearch(
        huid=UUID("86c4814b-feee-4ff0-b04d-4b3226318078"),
        ad_login=None,
        ad_domain=None,
        username="Test Bot",
        company=None,
        company_position=None,
        department=None,
        emails=[],
        other_id=None,
        user_kind=UserKinds.BOT,
    )

    bot.search_user_by_huid = AsyncMock(return_value=bot_user)  # type: ignore

    # - Act -
    with pytest.raises(UserIsBotError):
        await search_user_on_each_cts(bot, UUID("86c4814b-feee-4ff0-b04d-4b3226318078"))


async def test_search_user_on_each_cts_not_found(
    bot: Bot,
) -> None:
    # - Arrange -
    bot.search_user_by_huid = AsyncMock(  # type: ignore
        side_effect=UserNotFoundError("not found")
    )

    # - Act -
    search_result = await search_user_on_each_cts(
        bot, UUID("86c4814b-feee-4ff0-b04d-4b3226318078")
    )

    # - Assert -
    assert search_result is None


async def test_search_user_on_each_cts_suceed(
    bot: Bot,
) -> None:
    # - Arrange -
    user = UserFromSearch(
        huid=UUID("86c4814b-feee-4ff0-b04d-4b3226318078"),
        ad_login=None,
        ad_domain=None,
        username="Test User",
        company=None,
        company_position=None,
        department=None,
        emails=[],
        other_id=None,
        user_kind=UserKinds.CTS_USER,
    )

    bot.search_user_by_huid = AsyncMock(return_value=user)  # type: ignore

    # - Act -
    search_result = await search_user_on_each_cts(
        bot, UUID("86c4814b-feee-4ff0-b04d-4b3226318078")
    )

    # - Assert -
    assert search_result

    found_user, bot_account = search_result
    assert found_user is user
    assert bot_account is list(bot.bot_accounts)[0]
