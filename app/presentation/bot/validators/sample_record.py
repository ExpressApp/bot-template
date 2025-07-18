import orjson
from orjson import JSONDecodeError
from pybotx import IncomingMessage
from pydantic import ValidationError

from app.decorators.exceptions_mapper import exception_mapper
from app.presentation.bot.schemas.sample_record import SampleRecordCreateRequestSchema
from app.presentation.bot.validators.base import IBotRequestParser
from app.presentation.bot.validators.exceptions import MessageValidationError


class SampleRecordJsonCreateRequestValidator(
    IBotRequestParser[SampleRecordCreateRequestSchema]
):
    @exception_mapper(
        catch_exceptions=(JSONDecodeError, ValidationError),
        raise_exception=MessageValidationError,
    )
    def parse(self, raw_input: IncomingMessage) -> SampleRecordCreateRequestSchema:
        message_json = orjson.loads(raw_input.argument)
        # TODO replace to model_validate during migration to pydantic 2.0
        return SampleRecordCreateRequestSchema.parse_obj(message_json)
