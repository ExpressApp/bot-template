from orjson import orjson, JSONDecodeError
from pybotx import IncomingMessage
from pydantic import ValidationError

from app.presentation.bot.schemas.sample_record import SampleRecordCreateRequestSchema
from app.presentation.validators.base import IBotRequestParser
from app.presentation.validators.exceptions import MessageValidationError
from app.utils.exceptions_mapper import exception_mapper


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
