import pytest
from botx import CommandTypes, MessageBuilder, TestClient


@pytest.mark.asyncio
async def test_message_from_external_cts(
    builder: MessageBuilder,
    botx_client: TestClient,
):
    builder.user.ad_domain = None
    builder.user.ad_login = None
    builder.body = "/help"
    builder.message.command.command_type = CommandTypes.user
    await botx_client.send_command(builder.message)
    body = botx_client.notifications[0].result.body

    assert body == "\n".join(
        [
            "Данный бот зарегистрирован на другом CTS.",
            "Перейдите по `меншну`, чтобы попасть к вашему боту",
        ]
    )

    builder.user.host = "cts.testing2.dev"
    await botx_client.send_command(builder.message)
    body = botx_client.notifications[1].result.body

    assert body == "\n".join(
        [
            "Данный бот зарегистрирован на другом CTS.",
            "Обратитесь к администратору, чтобы он зарегистрировал бота на вашем CTS",
        ]
    )
