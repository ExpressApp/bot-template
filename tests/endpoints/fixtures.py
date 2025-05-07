import copy
from typing import Any, Dict
from uuid import UUID

import pytest


@pytest.fixture
def base_command_payload(bot_id: UUID) -> Dict[str, Any]:
    """Define the base command payload with a common structure."""
    return {
        "bot_id": str(bot_id),
        "command": {
            "body": "/debug",
            "command_type": "user",
            "data": {},
            "metadata": {},
        },
        "entities": [],
        "source_sync_id": None,
        "sync_id": "6f40a492-4b5f-54f3-87ee-77126d825b51",
        "from": {
            "ad_domain": None,
            "ad_login": None,
            "app_version": None,
            "chat_type": "chat",
            "device": None,
            "device_meta": {
                "permissions": None,
                "pushes": False,
                "timezone": "Europe/Moscow",
            },
            "device_software": None,
            "group_chat_id": "30dc1980-643a-00ad-37fc-7cc10d74e935",
            "host": "cts.example.com",
            "is_admin": True,
            "is_creator": True,
            "locale": "en",
            "manufacturer": None,
            "platform": None,
            "platform_package_id": None,
            "user_huid": "f16cdc5f-6366-5552-9ecd-c36290ab3d11",
            "username": None,
        },
    }


@pytest.fixture
def command_payload_v4(base_command_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Command payload with protocol version 4."""
    payload = copy.deepcopy(base_command_payload)
    payload.update(
        {
            "attachments": [],
            "async_files": [],
            "proto_version": 4,
        }
    )
    return payload


@pytest.fixture
def command_payload_v3(base_command_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Command payload with protocol version 3."""
    payload = copy.deepcopy(base_command_payload)
    payload.update(
        {
            "file": None,
            "proto_version": 3,
        }
    )

    return payload


@pytest.fixture
def unknown_bot_payload(command_payload_v4: Dict[str, Any]) -> Dict[str, Any]:
    """Command payload with unknown bot ID."""
    payload = copy.deepcopy(command_payload_v4)
    payload["bot_id"] = "c755e147-30a5-45df-b46a-c75aa6089c8f"

    return payload
