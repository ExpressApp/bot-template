"""Bot dependency for FastAPI."""

from fastapi import Depends, Request
from pybotx import Bot

import tests.integration.conftest


def get_bot(request: Request) -> Bot:
    if not isinstance(bot := request.app.state.bot, Bot):
        raise RuntimeError(f"request.app.state.bot should be Bot instance. ")

    return bot


bot_dependency = Depends(get_bot)
