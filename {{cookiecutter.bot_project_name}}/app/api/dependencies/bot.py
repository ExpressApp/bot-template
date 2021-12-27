"""Bot dependency for FastAPI."""

from botx import Bot
from fastapi import Depends, Request


def get_bot(request: Request) -> Bot:
    assert isinstance(request.app.state.bot, Bot)

    return request.app.state.bot


bot_dependency = Depends(get_bot)
