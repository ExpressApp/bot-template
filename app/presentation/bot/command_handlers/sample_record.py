from pybotx import Bot, IncomingMessage

from app.application.repository.exceptions import RecordCreateError, \
    RecordAlreadyExistsError, ValidationError
from app.application.use_cases.interfaces import ISampleRecordUseCases
from app.presentation.bot.command_handlers.base_handler import BaseCommandHandler
from app.presentation.bot.error_handlers.exceptions_chain_executor import (
    ExceptionHandlersChainExecutor, DEFAULT_HANDLERS,
)
from app.presentation.bot.error_handlers.base_handlers import \
    SendErrorExplainToUserHandler
from app.presentation.bot.resources.strings import SAMPLE_RECORD_CREATED_ANSWER
from app.presentation.bot.schemas.sample_record import SampleRecordCreateRequestSchema
from app.presentation.bot.validators.base import BotXJsonRequestParser


class CreateSampleRecordHandler(BaseCommandHandler):
    incoming_argument_parser = BotXJsonRequestParser(SampleRecordCreateRequestSchema)

    _EXCEPTIONS_HANDLERS = DEFAULT_HANDLERS + [
        SendErrorExplainToUserHandler(
            exception_explain_mapping={
                RecordAlreadyExistsError: "Запись с такими параметрами уже существует",
                RecordCreateError: "Внутренняя ошибка создания записи",
                ValidationError: "Неправильный формат данных"
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
        use_cases: ISampleRecordUseCases,
    ):
        self._use_cases = use_cases

        super().__init__(bot, message, self.exception_handler_chain_executor)

    async def handle_logic(
        self,
        request_parameter: SampleRecordCreateRequestSchema,  # type: ignore
    ) -> None:
        created_record = await self._use_cases.create_record(request_parameter)
        await self._bot.answer_message(
            SAMPLE_RECORD_CREATED_ANSWER.format(**created_record.dict())
        )
