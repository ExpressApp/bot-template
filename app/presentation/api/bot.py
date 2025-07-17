"""Bot dependency for FastAPI."""

from fastapi import Depends, Request
from pybotx import Bot


def get_bot(request: Request) -> Bot:
    assert isinstance(request.app.state.bot, Bot)

    return request.app.state.bot


bot_dependency = Depends(get_bot)
