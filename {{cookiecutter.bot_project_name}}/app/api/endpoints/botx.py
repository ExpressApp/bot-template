"""Endpoints for communication with botx."""

from botx import IncomingMessage, Status
from botx.models.status import StatusRecipient
from fastapi import APIRouter, Depends
from loguru import logger
from starlette.status import HTTP_202_ACCEPTED

from app.api.dependencies.status_recipient import get_status_recipient
from app.bot.bot import bot
from app.schemas.notification_callback import (
    BaseCallback,
    ErrorCallback,
    SuccessCallback,
)

router = APIRouter()


@router.post("/command", name="botx:command", status_code=HTTP_202_ACCEPTED)
async def bot_command(message: IncomingMessage) -> None:
    """Receive commands from users. Max timeout - 5 seconds."""
    await bot.execute_command(message.dict())


@router.get("/status", name="botx:status", response_model=Status)
async def bot_status(
    recipient: StatusRecipient = Depends(get_status_recipient),
) -> Status:
    """Send commands with short descriptions."""
    return await bot.status()


@router.post(
    "/notification/callback", name="botx:callback", status_code=HTTP_202_ACCEPTED
)
async def bot_callback(callback: BaseCallback) -> None:
    """Receive callbacks for async methods."""
    payload = callback.dict()
    if isinstance(callback, SuccessCallback):
        logger.bind(payload=payload).debug("Received succsess callback.")
    elif isinstance(callback, ErrorCallback):
        logger.bind(payload=payload).warning("Received error callback.")
