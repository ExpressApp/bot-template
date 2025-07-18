from pybotx import Bot, IncomingMessage

from app.application.use_cases.interfaces import ISampleRecordUseCases
from app.presentation.bot.handlers.command import BaseCommandHandler
from app.presentation.bot.resources.strings import SAMPLE_RECORD_CREATED_ANSWER
from app.presentation.bot.schemas.sample_record import SampleRecordCreateRequestSchema
from app.presentation.bot.validators.base import BotXJsonRequestParser


class CreateSampleRecordHandler(BaseCommandHandler):
    incoming_argument_parser = BotXJsonRequestParser(SampleRecordCreateRequestSchema)

    def __init__(
        self,
        bot: Bot,
        message: IncomingMessage,
        use_cases: ISampleRecordUseCases,
    ):
        self._use_cases = use_cases
        super().__init__(bot, message)

    async def handle_logic(
        self,
        request_parameter: SampleRecordCreateRequestSchema,  # type: ignore
    ) -> None:
        created_record = await self._use_cases.create_record(request_parameter)
        await self._bot.answer_message(
            SAMPLE_RECORD_CREATED_ANSWER.format(**created_record.dict())
        )
