"""Dependency related to database."""

from botx import Bot, Depends

from app.db.sqlalchemy import AsyncSessionFactory


def get_session_factory(bot: Bot) -> AsyncSessionFactory:
    return bot.state.session_factory


session_factory_dependency = Depends(get_session_factory)
