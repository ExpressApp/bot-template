import pytest
from botx import ChatCreatedEvent, SystemEvents
from botx.testing import MessageBuilder, TestClient as BotXClient


@pytest.mark.asyncio
async def test_default_handler(builder: MessageBuilder, botx_client: BotXClient):
    text = "random text"
    builder.body = text
    await botx_client.send_command(builder.message)

    assert len(botx_client.command_results) == 0


@pytest.mark.asyncio
async def test_chat_created(
    builder: MessageBuilder,
    botx_client: BotXClient,
    chat_created_data: ChatCreatedEvent,
):
    builder.command_data = chat_created_data.dict()
    builder.body = SystemEvents.chat_created.value
    builder.user.user_huid = None
    builder.user.ad_login = None
    builder.user.ad_domain = None
    builder.user.username = None

    builder.system_command = True

    await botx_client.send_command(builder.message)

    result = botx_client.notifications[0].result

    assert result.body == (
        "Вас приветствует {{cookiecutter.bot_name}}!\n\n"
        "Для более подробной информации нажмите кнопку `/help`"
    )

    help_bubble = result.bubble[0][0]

    assert help_bubble.command == "/help"
    assert help_bubble.label == "/help"


@pytest.mark.asyncio
async def test_help_command(builder: MessageBuilder, botx_client: BotXClient):
    builder.body = "/help"

    await botx_client.send_command(builder.message)

    body = botx_client.notifications[0].result.body

    assert body == "Справка по командам:\n\n`/help` - Справка по командам."
