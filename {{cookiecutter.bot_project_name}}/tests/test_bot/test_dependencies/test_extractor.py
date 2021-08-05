import pytest
from botx import Bot, MessageBuilder

from app.bot.dependencies.extractor import DataExtractor


@pytest.mark.asyncio
async def test_extractor(builder: MessageBuilder, bot: Bot):
    message = builder.message.command
    message.data = {"test": "passed"}

    assert DataExtractor("test")(message) == "passed"
