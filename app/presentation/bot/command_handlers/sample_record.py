from typing import Callable

from pybotx import Bot, IncomingMessage

from app.application.repository.exceptions import (
    RecordAlreadyExistsError,
    RecordCreateError,
    RecordDoesNotExistError,
)
from app.application.repository.interfaces import (
    ISampleRecordRepository,
    ISampleRecordUnitOfWork,
)
from app.application.use_cases.interfaces import ISampleRecordUseCases
from app.presentation.bot.command_handlers.base_handler import BaseCommandHandler
from app.presentation.bot.error_handlers.base_handlers import (
    SendErrorExplainToUserHandler,
)
from app.presentation.bot.error_handlers.exceptions_chain_executor import (
    DEFAULT_HANDLERS_WITH_EXPLAIN,
    ExceptionHandlersChainExecutor,
)
from app.presentation.bot.resources.strings import (
    SAMPLE_RECORD_CREATED_ANSWER,
    SAMPLE_RECORD_DELETED_ANSWER,
    SHOW_SAMPLE_RECORD_ANSWER,
)
from app.presentation.bot.schemas.sample_record import (
    SampleRecordCreateRequestSchema,
    SampleRecordGetOrDeleteRequestSchema,
)
from app.presentation.bot.validators.base import (
    BotXJsonRequestParser,
    BotXPlainRequestParser,
)
from app.presentation.bot.validators.exceptions import MessageValidationError


class CreateSampleRecordHandler(BaseCommandHandler):
    incoming_argument_parser = BotXJsonRequestParser(SampleRecordCreateRequestSchema)

    _EXCEPTIONS_HANDLERS = DEFAULT_HANDLERS_WITH_EXPLAIN + [
        SendErrorExplainToUserHandler(
            exception_explain_mapping={
                RecordAlreadyExistsError: "Запись с такими параметрами уже существует",
                RecordCreateError: "Внутренняя ошибка создания записи",
                MessageValidationError: "Неправильный формат данных",
            }
        )
    ]

    def __init__(
        self,
        bot: Bot,
        message: IncomingMessage,
        unit_of_work: ISampleRecordUnitOfWork,
        use_case_factory: Callable[[ISampleRecordRepository], ISampleRecordUseCases],
    ):
        self._use_cases = use_case_factory
        self.unit_of_work = unit_of_work

        exception_handler_chain_executor = ExceptionHandlersChainExecutor(
            self._EXCEPTIONS_HANDLERS
        )

        super().__init__(bot, message, exception_handler_chain_executor)

    async def handle_logic(
        self,
        request_parameter: SampleRecordCreateRequestSchema,  # type: ignore
    ) -> None:
        async with self.unit_of_work as uof:
            use_case = self._use_cases(uof.get_sample_record_repository())
            created_record = await use_case.create_record(request_parameter)

        await self._bot.answer_message(
            SAMPLE_RECORD_CREATED_ANSWER.format(
                id=created_record.id,
                record_data=created_record.record_data,
                name=created_record.name,
            )
        )


class DeleteSampleRecordHandler(BaseCommandHandler):
    incoming_argument_parser = BotXPlainRequestParser(
        SampleRecordGetOrDeleteRequestSchema
    )

    _EXCEPTIONS_HANDLERS = DEFAULT_HANDLERS_WITH_EXPLAIN + [
        SendErrorExplainToUserHandler(
            exception_explain_mapping={
                RecordDoesNotExistError: "Запиcь с указанным id не найдена",
                MessageValidationError: "Неправильный формат данных",
            }
        )
    ]

    def __init__(
        self,
        bot: Bot,
        message: IncomingMessage,
        unit_of_work: ISampleRecordUnitOfWork,
        use_case_factory: Callable[[ISampleRecordRepository], ISampleRecordUseCases],
    ):
        self._use_cases = use_case_factory
        self.unit_of_work = unit_of_work
        exception_handler_chain_executor = ExceptionHandlersChainExecutor(
            self._EXCEPTIONS_HANDLERS
        )

        super().__init__(bot, message, exception_handler_chain_executor)

    async def handle_logic(
        self,
        request_parameter: SampleRecordGetOrDeleteRequestSchema,  # type: ignore
    ) -> None:
        async with self.unit_of_work as uof:
            await self._use_cases(uof.get_sample_record_repository()).delete_record(
                request_parameter.id
            )

        await self._bot.answer_message(
            SAMPLE_RECORD_DELETED_ANSWER.format(
                id=request_parameter.id,
            )
        )


class GetSampleRecordHandler(BaseCommandHandler):
    incoming_argument_parser = BotXPlainRequestParser(
        SampleRecordGetOrDeleteRequestSchema
    )

    _EXCEPTIONS_HANDLERS = DEFAULT_HANDLERS_WITH_EXPLAIN + [
        SendErrorExplainToUserHandler(
            exception_explain_mapping={
                RecordDoesNotExistError: "Запиcь с указанным id не найдена",
                MessageValidationError: "Неправильный формат данных",
            }
        )
    ]
    exception_handler_chain_executor = ExceptionHandlersChainExecutor(
        _EXCEPTIONS_HANDLERS
    )

    def __init__(
        self,
        bot: Bot,
        message: IncomingMessage,
        unit_of_work: ISampleRecordUnitOfWork,
        use_case_factory: Callable[[ISampleRecordRepository], ISampleRecordUseCases],
    ):
        self._use_cases = use_case_factory
        self.unit_of_work = unit_of_work

        exception_handler_chain_executor = ExceptionHandlersChainExecutor(
            self._EXCEPTIONS_HANDLERS
        )

        super().__init__(bot, message, exception_handler_chain_executor)

    async def handle_logic(
        self,
        request_parameter: SampleRecordGetOrDeleteRequestSchema,
    ) -> None:
        async with self.unit_of_work as uof:
            record = await self._use_cases(
                uof.get_sample_record_repository()
            ).get_record(request_parameter.id)

        await self._bot.answer_message(
            SHOW_SAMPLE_RECORD_ANSWER.format(
                id=record.id,
                record_data=record.record_data,
                name=record.name,
            )
        )
