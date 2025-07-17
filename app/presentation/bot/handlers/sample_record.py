from pybotx import Bot, IncomingMessage

from app.application.use_cases.interfaces import ISampleRecordUseCases
from app.presentation.bot.handlers.command import BaseCommandHandler
from app.presentation.bot.validators.base import BotXJsonRequestParser
from app.presentation.bot.resources.strings import SAMPLE_RECORD_CREATED_ANSWER
from app.presentation.bot.schemas.sample_record import SampleRecordCreateRequestSchema


class CreateSampleRecordHandler(BaseCommandHandler):
    def __init__(
        self,
        bot: Bot,
        message: IncomingMessage,
        use_cases: ISampleRecordUseCases,
    ):
        self._use_cases = use_cases
        super().__init__(bot, message)

    exception_explain_mapping = {}
    incoming_argument_parser = BotXJsonRequestParser(SampleRecordCreateRequestSchema)

    async def handle_logic(
        self,
        request_parameter: SampleRecordCreateRequestSchema,
    ) -> None:
        created_record = await self._use_cases.create_record(request_parameter)
        await self._bot.answer_message(
            SAMPLE_RECORD_CREATED_ANSWER.format(**created_record.dict())
        )
