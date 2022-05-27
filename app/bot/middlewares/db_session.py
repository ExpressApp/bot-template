"""Middleware for creating db_session per-request."""

from pybotx import Bot, IncomingMessage, IncomingMessageHandlerFunc


async def db_session_middleware(
    message: IncomingMessage, bot: Bot, call_next: IncomingMessageHandlerFunc
) -> None:
    session_factory = bot.state.db_session_factory

    async with session_factory() as db_session:
        message.state.db_session = db_session

        await call_next(message, bot)
        await db_session.commit()
