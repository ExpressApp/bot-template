"""Bot dependency for FastAPI."""
from typing import Optional

from fastapi import Depends, Request
from pybotx import Bot


def get_bot(request: Request) -> Bot:
    assert isinstance(request.app.state.bot, Bot)

    return request.app.state.bot


bot_dependency = Depends(get_bot)


async def check_db_connection(request: Request) -> Optional[str]:
    assert isinstance(request.app.state.bot, Bot)

    bot = request.app.state.bot
    session_factory = bot.state.db_session_factory

    async with session_factory() as db_session:
        try:
            await db_session.execute("SELECT 1")
        except Exception as exc:
            return str(exc)

    return None


check_db_connection_dependency = Depends(check_db_connection)


async def check_redis_connection(request: Request) -> Optional[str]:
    assert isinstance(request.app.state.bot, Bot)

    bot = request.app.state.bot
    return await bot.state.redis_repo.ping()


check_redis_connection_dependency = Depends(check_redis_connection)
