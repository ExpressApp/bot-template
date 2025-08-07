from typing import Callable

from dependency_injector.wiring import Provide, Provider, inject
from pybotx import Bot, HandlerCollector, IncomingMessage

from app.application.repository.interfaces import ISampleRecordRepository
from app.application.use_cases.interfaces import ISampleRecordUseCases
from app.infrastructure.containers import (
    BotSampleRecordCommandContainer,
)
from app.infrastructure.repositories.unit_of_work import (
    ReadOnlySampleRecordUnitOfWork,
    WriteSampleRecordUnitOfWork,
)
from app.presentation.bot.command_handlers.sample_record import (
    CreateSampleRecordHandler,
    DeleteSampleRecordHandler,
    GetSampleRecordHandler,
)
from app.presentation.bot.commands.command_listing import SampleRecordCommands

collector = HandlerCollector()

UseCaseFactory = Callable[[ISampleRecordRepository], ISampleRecordUseCases]


@collector.command(**SampleRecordCommands.CREATE_RECORD.command_data())
@inject
async def create_sample_record(
    message: IncomingMessage,
    bot: Bot,
    unit_of_work: WriteSampleRecordUnitOfWork = Provide[
        BotSampleRecordCommandContainer.rw_unit_of_work
    ],
    use_case_factory: UseCaseFactory = Provider[
        BotSampleRecordCommandContainer.record_use_cases_factory
    ],
) -> None:
    """Creates a sample record in the database."""
    handler = CreateSampleRecordHandler(
        bot=bot,
        message=message,
        use_case_factory=use_case_factory,
        unit_of_work=unit_of_work,
    )

    await handler.execute()


@collector.command(**SampleRecordCommands.DELETE_RECORD.command_data())
@inject
async def delete_sample_record(
    message: IncomingMessage,
    bot: Bot,
    unit_of_work: WriteSampleRecordUnitOfWork = Provide[
        BotSampleRecordCommandContainer.rw_unit_of_work
    ],
    use_case_factory: UseCaseFactory = Provider[
        BotSampleRecordCommandContainer.record_use_cases_factory
    ],
) -> None:
    """Delete a sample record in the database."""
    await DeleteSampleRecordHandler(
        bot=bot,
        message=message,
        use_case_factory=use_case_factory,
        unit_of_work=unit_of_work,
    ).execute()


@collector.command(**SampleRecordCommands.GET_RECORD.command_data())
@inject
async def get_sample_record(
    message: IncomingMessage,
    bot: Bot,
    unit_of_work: ReadOnlySampleRecordUnitOfWork = Provide[
        BotSampleRecordCommandContainer.ro_unit_of_work
    ],
    use_case_factory: UseCaseFactory = Provider[
        BotSampleRecordCommandContainer.record_use_cases_factory
    ],
) -> None:
    """Delete a sample record in the database."""
    await GetSampleRecordHandler(
        bot=bot,
        message=message,
        use_case_factory=use_case_factory,
        unit_of_work=unit_of_work,
    ).execute()
