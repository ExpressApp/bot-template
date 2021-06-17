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
            "Для продолжения работы напишите боту со своего CTS.",
            "Найти его можно через поиск корпоративных контактов.",
        ]
    )
