import pytest
from botx import Bot
from botx.models.menu import MenuCommand


@pytest.mark.asyncio
async def test_command_sequence(bot: Bot):
    bot_commands = (await bot.status()).result.commands

    help_command = MenuCommand(
        description="Показать список команд",
        body="/help",
        name="help",
        options={},
        elements=[],
    )
    command_list = [help_command]

    assert bot_commands == command_list
