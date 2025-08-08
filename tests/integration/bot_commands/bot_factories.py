from typing import Any, Optional
from uuid import UUID

import factory
from factory import Factory
from pybotx import (
    BotAccount,
    Chat,
    ChatTypes,
    ClientPlatforms,
    IncomingMessage,
    UserDevice,
    UserSender,
)


class BotAccountFactory(Factory):
    """Factory for bot accounts."""

    id: UUID = factory.Faker("uuid4")  # type:ignore
    host: str | None = None

    class Meta:
        model = BotAccount


class ChatFactory(Factory):
    """Factory for chats."""

    id: UUID = factory.Faker("uuid4")  # type:ignore
    type: ChatTypes = ChatTypes.PERSONAL_CHAT

    class Meta:
        model = Chat


class UserDeviceFactory(Factory):
    """Factory for user devices."""

    manufacturer: str | None = None
    device_name: str | None = None
    os: str | None = None
    pushes: str | None = None
    timezone: str | None = None
    permissions: str | None = None
    platform: ClientPlatforms | None = None
    platform_package_id: str | None = None
    app_version: str | None = None
    locale: str | None = None

    class Meta:
        model = UserDevice


class UserSenderFactory(Factory):
    """Factory for user senders."""

    huid: UUID = factory.Faker("uuid4")  # type:ignore
    udid = None
    ad_login: Optional[str] = None
    ad_domain: Optional[str] = None
    username: Optional[str] = None
    is_chat_admin: bool = True
    is_chat_creator: bool = True
    device: UserDevice = factory.SubFactory(UserDeviceFactory)  # type:ignore

    class Meta:
        model = UserSender


class IncomingMessageFactory(Factory):
    """Factory for incoming messages."""

    bot: BotAccount = factory.SubFactory(BotAccountFactory)  # type: ignore
    sync_id: UUID = factory.Faker("uuid4")  # type: ignore
    source_sync_id: Optional[UUID] = None
    body: str = factory.Faker("text", max_nb_chars=100)  # type: ignore
    data: dict[str, Any] = {}
    metadata: dict = {}
    sender: UserSender = factory.SubFactory(UserSenderFactory)  # type: ignore
    chat: Chat = factory.SubFactory(ChatFactory)  # type: ignore
    raw_command: Optional[str] = None

    class Meta:
        model = IncomingMessage
