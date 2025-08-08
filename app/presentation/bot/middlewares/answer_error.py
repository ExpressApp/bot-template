"""Middleware to handle AnswerError and AnswerMessageError exceptions."""

from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pybotx import (
    Bot,
    BubbleMarkup,
    IncomingMessage,
    IncomingMessageHandlerFunc,
    KeyboardMarkup,
    OutgoingAttachment,
    OutgoingMessage,
)
from pybotx.missing import Missing, Undefined
from pybotx.models.attachments import IncomingFileAttachment


async def answer_error_middleware(
    message: IncomingMessage, bot: Bot, call_next: IncomingMessageHandlerFunc
) -> None:
    """Middleware, used for answering error messages to user.."""
    try:
        await call_next(message, bot)
    except AnswerError as exc:
        await bot.send(
            message=exc.message,
            wait_callback=exc.wait_callback,
            callback_timeout=exc.callback_timeout,
        )
    except AnswerMessageError as exc:
        await bot.answer_message(
            body=exc.body,
            metadata=exc.metadata,
            bubbles=exc.bubbles,
            keyboard=exc.keyboard,
            file=exc.file,
            recipients=exc.recipients,
            silent_response=exc.silent_response,
            markup_auto_adjust=exc.markup_auto_adjust,
            stealth_mode=exc.stealth_mode,
            send_push=exc.send_push,
            ignore_mute=exc.ignore_mute,
            wait_callback=exc.wait_callback,
            callback_timeout=exc.callback_timeout,
        )


class AnswerMessageError(Exception):
    def __init__(
        self,
        body: str,
        *,
        metadata: Missing[Dict[str, Any]] = Undefined,
        bubbles: Missing[BubbleMarkup] = Undefined,
        keyboard: Missing[KeyboardMarkup] = Undefined,
        file: Missing[Union[IncomingFileAttachment, OutgoingAttachment]] = Undefined,
        recipients: Missing[List[UUID]] = Undefined,
        silent_response: Missing[bool] = Undefined,
        markup_auto_adjust: Missing[bool] = Undefined,
        stealth_mode: Missing[bool] = Undefined,
        send_push: Missing[bool] = Undefined,
        ignore_mute: Missing[bool] = Undefined,
        wait_callback: bool = True,
        callback_timeout: Optional[float] = None,
    ):
        self.body = body
        self.metadata = metadata
        self.bubbles = bubbles
        self.keyboard = keyboard
        self.file = file
        self.recipients = recipients
        self.silent_response = silent_response
        self.markup_auto_adjust = markup_auto_adjust
        self.stealth_mode = stealth_mode
        self.send_push = send_push
        self.ignore_mute = ignore_mute
        self.wait_callback = wait_callback
        self.callback_timeout = callback_timeout

        super().__init__()


class AnswerError(Exception):
    def __init__(
        self,
        *,
        message: OutgoingMessage,
        wait_callback: bool = True,
        callback_timeout: Optional[float] = None,
    ):
        self.message = message
        self.wait_callback = wait_callback
        self.callback_timeout = callback_timeout

        super().__init__()
