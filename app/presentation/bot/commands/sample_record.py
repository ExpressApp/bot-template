from typing import Callable

from dependency_injector.providers import Factory
from dependency_injector.wiring import Provider, inject, Provide
from pybotx import Bot, HandlerCollector, IncomingMessage
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.repository.interfaces import ISampleRecordRepository
from app.application.use_cases.interfaces import ISampleRecordUseCases
from app.infrastructure.containers import (
    BotSampleRecordCommandContainer,
    ApplicationStartupContainer,
)
from app.infrastructure.db.sqlalchemy import provide_session
from app.infrastructure.repositories.unit_of_work import WriteSampleRecordUnitOfWork
from app.presentation.bot.commands.command_listing import SampleRecordCommands
from app.presentation.bot.command_handlers.sample_record import (
    CreateSampleRecordHandler,
    DeleteSampleRecordHandler,
)

collector = HandlerCollector()


@collector.command(**SampleRecordCommands.CREATE_RECORD.command_data())
# @provide_session
@inject
async def create_sample_record(
    message: IncomingMessage,
    bot: Bot,
    # session: AsyncSession,
    unit_of_work: WriteSampleRecordUnitOfWork=Provide[BotSampleRecordCommandContainer.rw_unit_of_work],
    record_use_cases_factory: Callable[[ISampleRecordRepository], ISampleRecordUseCases] = Provider[
        BotSampleRecordCommandContainer.record_use_cases_factory
    ],
) -> None:
    """Creates a sample record in the database."""
    handler = CreateSampleRecordHandler(
        bot=bot,
        message=message,
        use_case_factory=record_use_cases_factory,
        unit_of_work=unit_of_work,
    )

    await handler.execute()


@collector.command(**SampleRecordCommands.DELETE_RECORD.command_data())
# @provide_session
@inject
async def delete_sample_record(
    message: IncomingMessage,
    bot: Bot,
    session: AsyncSession,
    record_use_cases_factory: Factory[ISampleRecordUseCases] = Provider[
        BotSampleRecordCommandContainer.record_use_cases_factory
    ],
) -> None:
    """Delete a sample record in the database."""
    await DeleteSampleRecordHandler(
        bot=bot,
        message=message,
        use_cases=record_use_cases_factory(session),
    ).execute()
