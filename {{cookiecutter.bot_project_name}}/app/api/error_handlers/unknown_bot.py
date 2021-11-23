"""Definition for error handler for message from unregistered CTS."""

from botx import BotDisabledErrorData, BotDisabledResponse, UnknownBotError
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.status import HTTP_503_SERVICE_UNAVAILABLE


async def message_from_unknown_bot_handler(
    _request: Request, exc: UnknownBotError
) -> Response:
    """Handle error for message from unknown bot."""
    return JSONResponse(
        status_code=HTTP_503_SERVICE_UNAVAILABLE,
        content=BotDisabledResponse(
            error_data=BotDisabledErrorData(
                status_message=f"Unknown bot ID: {exc.bot_id}"
            )
        ).dict(),
    )
