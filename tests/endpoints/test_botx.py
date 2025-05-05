import asyncio
from http import HTTPStatus
from typing import Any, Dict
from uuid import UUID

import httpx
import respx
from fastapi.testclient import TestClient
from pybotx import Bot

from app.main import get_application


@respx.mock
def test__web_app__bot_status_response_ok(
    bot_id: UUID,
    bot: Bot,
    authorization_header: Dict[str, str],
) -> None:
    # - Arrange -
    query_params = {
        "bot_id": str(bot_id),
        "chat_type": "chat",
        "user_huid": "f16cdc5f-6366-5552-9ecd-c36290ab3d11",
    }

    # - Act -
    with TestClient(get_application()) as test_client:
        response = test_client.get(
            "/status",
            params=query_params,
            headers=authorization_header,
        )

    # - Assert -
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "result": {
            "commands": [
                {
                    "body": "/help",
                    "description": "Get available commands",
                    "name": "/help",
                }
            ],
            "enabled": True,
            "status_message": "Bot is working",
        },
        "status": "ok",
    }


@respx.mock
def test__web_app__bot_status_unknown_bot_response_service_unavailable(
    bot_id: UUID,
    bot: Bot,
    authorization_header: Dict[str, str],
) -> None:
    # - Arrange -
    query_params = {
        "bot_id": "f3e176d5-ff46-4b18-b260-25008338c06e",
        "chat_type": "chat",
        "user_huid": "f16cdc5f-6366-5552-9ecd-c36290ab3d11",
    }

    # - Act -
    with TestClient(get_application()) as test_client:
        response = test_client.get(
            "/status",
            params=query_params,
            headers=authorization_header,
        )

    # - Assert -
    assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE

    status_message = response.json()["error_data"]["status_message"]
    assert status_message == "Unknown bot_id: f3e176d5-ff46-4b18-b260-25008338c06e"


@respx.mock
def test__web_app__bot_status_without_parameters_response_bad_request(
    bot_id: UUID,
    bot: Bot,
    authorization_header: Dict[str, str],
) -> None:
    # - Arrange -
    query_params: Dict[str, str] = {}

    # - Act -
    with TestClient(get_application()) as test_client:
        response = test_client.get(
            "/status",
            params=query_params,
            headers=authorization_header,
        )

    # - Assert -
    assert response.status_code == HTTPStatus.BAD_REQUEST

    status_message = response.json()["error_data"]["status_message"]
    assert status_message == "Invalid params"


@respx.mock
async def test__web_app__bot_command_response_accepted(
    bot_id: UUID,
    host: str,
    bot: Bot,
    authorization_header: Dict[str, str],
    command_payload_v4: Dict[str, Any],
) -> None:
    # - Arrange -
    direct_notification_endpoint = respx.post(
        f"https://{host}/api/v4/botx/notifications/direct",
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e7"},
            },
        ),
    )

    callback_payload = {
        "status": "ok",
        "sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e7",
        "result": {},
    }

    # - Act -
    with TestClient(get_application()) as test_client:
        command_response = test_client.post(
            "/command",
            json=command_payload_v4,
            headers=authorization_header,
        )

        max_attempts = 5
        for attempt in range(max_attempts):
            # Services are not always available within 0.1 seconds.
            callback_response = test_client.post(
                "/notification/callback",
                json=callback_payload,
            )
            if callback_response.status_code == HTTPStatus.SERVICE_UNAVAILABLE:
                await asyncio.sleep(0.1 * (attempt + 1))
            else:
                break

    # - Assert -
    assert command_response.status_code == HTTPStatus.ACCEPTED
    assert direct_notification_endpoint.called
    assert callback_response.status_code == HTTPStatus.ACCEPTED
    assert callback_response.json() == {"result": "accepted"}


@respx.mock
def test__web_app__bot_command_response_service_unavailable(
    bot_id: UUID,
    host: str,
    bot: Bot,
) -> None:
    # - Arrange -
    callback_payload = {
        "status": "ok",
        "sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
        "result": {},
    }

    # - Act -
    with TestClient(get_application()) as test_client:
        callback_response = test_client.post(
            "/notification/callback",
            json=callback_payload,
        )

    # - Assert -
    assert callback_response.status_code == HTTPStatus.SERVICE_UNAVAILABLE

    status_message = callback_response.json()["error_data"]["status_message"]
    assert status_message == (
        "Unexpected callback with sync_id: 21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"
    )


@respx.mock
def test__web_app__unknown_bot_response_service_unavailable(
    bot: Bot, authorization_header: Dict[str, str], unknown_bot_payload: Dict[str, Any]
) -> None:
    # - Act -
    with TestClient(get_application()) as test_client:
        response = test_client.post(
            "/command",
            json=unknown_bot_payload,
            headers=authorization_header,
        )

    # - Assert -
    assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE

    status_message = response.json()["error_data"]["status_message"]
    assert status_message == (
        "No credentials for bot c755e147-30a5-45df-b46a-c75aa6089c8f"
    )


@respx.mock
def test__web_app__unsupported_bot_api_version_service_unavailable(
    bot: Bot,
    authorization_header: Dict[str, str],
    command_payload_v3: Dict[str, Any],
) -> None:
    # - Act -
    with TestClient(get_application()) as test_client:
        response = test_client.post(
            "/command",
            json=command_payload_v3,
            headers=authorization_header,
        )

    # - Assert -
    assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE

    status_message = response.json()["error_data"]["status_message"]
    assert status_message == (
        "Unsupported Bot API version: `3`. "
        "Set protocol version to `4` in Admin panel."
    )
