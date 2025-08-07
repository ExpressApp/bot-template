from typing import Callable, Optional
from uuid import UUID, uuid4

import pytest
from pybotx import IncomingMessage, BotAccount, UserSender, UserDevice, Chat, ChatTypes

from tests.integration.bot_commands.bot_factories import IncomingMessageFactory


@pytest.fixture
def message_from_user(
    bot_id: UUID,
):
    return IncomingMessageFactory.create(
        bot__id=bot_id,
    )


@pytest.fixture
def command_message_from_user(
    bot_id: UUID,
) -> Callable[[str, str], IncomingMessage]:
    def factory(command: str, args: str) -> IncomingMessage:
        body = f"{command} {args}"
        return IncomingMessageFactory.create(bot__id=bot_id, body=body)

    return factory


@pytest.fixture
def create_sample_record_command_message_from_user_factory(
    command_message_from_user,
) -> Callable[[str], IncomingMessage]:
    def factory(args: str) -> IncomingMessage:
        return command_message_from_user("/create_record", args)

    return factory


@pytest.fixture
def delete_sample_record_command_message_from_user_factory(
    command_message_from_user,
) -> Callable[[int], IncomingMessage]:
    def factory(object_id: int) -> IncomingMessage:
        return command_message_from_user("/delete_record", str(object_id))

    return factory
