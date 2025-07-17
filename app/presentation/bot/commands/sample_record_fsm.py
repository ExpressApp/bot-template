from dependency_injector.wiring import inject, Provider
from pybotx import HandlerCollector, Bot, IncomingMessage
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.containers import BotSampleRecordCommandContainer
from app.infrastructure.db.sqlalchemy import provide_session
from app.presentation.bot.commands.command_listing import SampleRecordCommands
from app.presentation.bot.handlers import CreateSampleRecordHandler

collector = HandlerCollector()


@collector.command(**SampleRecordCommands.CREATE_RECORD.command_data())
@provide_session
@inject
async def create_sample_record_with_fsm(
    message: IncomingMessage,
    bot: Bot,
    session: AsyncSession,
    record_use_cases_factory=Provider[
        BotSampleRecordCommandContainer.record_use_cases_factory
    ],
):
    await CreateSampleRecordHandler(
        bot=bot, message=message, use_cases=record_use_cases_factory.provider(session)
    ).execute()
