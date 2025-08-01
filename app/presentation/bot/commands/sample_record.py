from dependency_injector.providers import Factory
from dependency_injector.wiring import Provider, inject
from pybotx import Bot, HandlerCollector, IncomingMessage
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.interfaces import ISampleRecordUseCases
from app.infrastructure.containers import BotSampleRecordCommandContainer
from app.infrastructure.db.sqlalchemy import provide_transaction_session
from app.presentation.bot.commands.command_listing import SampleRecordCommands
from app.presentation.bot.handlers.sample_record import CreateSampleRecordHandler

collector = HandlerCollector()


@collector.command(**SampleRecordCommands.CREATE_RECORD.command_data())
@provide_transaction_session
@inject
async def create_sample_record(
    message: IncomingMessage,
    bot: Bot,
    session: AsyncSession,
    record_use_cases_factory: Factory[ISampleRecordUseCases] = Provider[
        BotSampleRecordCommandContainer.record_use_cases_factory
    ],
) -> None:
    """Creates a sample record in the database."""
    await CreateSampleRecordHandler(
        bot=bot, message=message, use_cases=record_use_cases_factory.provider(session)
    ).execute()
