import orjson
from orjson import JSONDecodeError
from pybotx import IncomingMessage
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.decorators.exception_mapper import ExceptionMapper, EnrichedExceptionFactory
from app.presentation.bot.schemas.sample_record import SampleRecordCreateRequestSchema
from app.presentation.bot.validators.base import IBotRequestParser
from app.presentation.bot.validators.exceptions import MessageValidationError


class SampleRecordJsonCreateRequestValidator(
    IBotRequestParser[SampleRecordCreateRequestSchema]
):
    @ExceptionMapper(
        {
            (JSONDecodeError, ValidationError): EnrichedExceptionFactory(
                MessageValidationError
            )
        },
        is_bound_method=True,
    )
    def parse(self, raw_input: IncomingMessage) -> SampleRecordCreateRequestSchema:
        message_json = orjson.loads(raw_input.argument)
        # TODO replace to model_validate during migration to pydantic 2.0
        return SampleRecordCreateRequestSchema.parse_obj(message_json)
